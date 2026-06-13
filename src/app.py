import sys
import traceback
import collections
import collections.abc
from pathlib import Path

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    collections.Mapping = collections.abc.Mapping
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Iterable = collections.abc.Iterable
    collections.Iterator = collections.abc.Iterator
    collections.KeysView = collections.abc.KeysView
    collections.ValuesView = collections.abc.ValuesView

from flask import Flask, render_template, request
from werkzeug.utils import secure_filename

from config import GLASSES_DATA_PATH, IMAGE_PATH, UPLOAD_DIR
from face_analyzer import FaceAnalyzer
from glasses_loader import GlassesDataLoader
from scoring_engine import SmartGlassesRecommendationSystem
from confidence_engine import EnhancedGlassesKBS

from facts import (
    FaceShape,
    FaceDimensions,
    PersonInfo,
    UserPreferences,
    ProfessionalPreferences,
    AthleticPreferences,
    ArtisticPreferences,
    StylePreference,
    ActivityLevel,
    DesignPreference,
    PathSelected,
    GlassFrame,
    FinalRecommendation,
    FinalRecommendationWithCF,
    UncertaintyEvidence,
    State,
)

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_image():
    image_file = request.files.get("image")

    if not image_file or image_file.filename == "":
        return IMAGE_PATH

    filename = secure_filename(image_file.filename)
    suffix = Path(filename).suffix.lower()

    if suffix not in [".png", ".jpg", ".jpeg"]:
        raise ValueError("Only PNG, JPG, and JPEG images are supported.")

    image_path = UPLOAD_DIR / f"uploaded_face{suffix}"
    image_file.save(image_path)

    return str(image_path)


def build_user_facts(form):
    facts = []

    gender = form.get("gender")
    path = form.get("path")

    if gender:
        facts.append(PersonInfo(gender=gender))

    if path:
        facts.append(PathSelected(path_type=path))

    professional_priority = form.get("professional_priority")
    if professional_priority:
        facts.append(
            ProfessionalPreferences(professional_priority=professional_priority)
        )

    style_preference = form.get("style_preference")
    if style_preference:
        facts.append(StylePreference(style=style_preference))

    comfort_issue = form.get("comfort_issue")
    if comfort_issue:
        if comfort_issue in ["slips_down", "sits_high"]:
            facts.append(UserPreferences(bridge_fit=comfort_issue))
        elif comfort_issue == "lightweight":
            facts.append(UserPreferences(weight_pref="lightweight"))

    activity_level = form.get("activity_level")
    if activity_level:
        facts.append(ActivityLevel(level=activity_level))

    concern = form.get("concern")
    if concern:
        facts.append(AthleticPreferences(concern=concern))

    stability_design = form.get("stability_design")
    if stability_design:
        facts.append(AthleticPreferences(stability_design=stability_design))

    durability_priority = form.get("durability_priority")
    if durability_priority:
        if durability_priority == "lightweight":
            facts.append(UserPreferences(weight_pref="lightweight"))
        elif durability_priority == "durable":
            facts.append(UserPreferences(durability_priority="durable"))

    light_material = form.get("light_material")
    if light_material:
        facts.append(UserPreferences(light_material=light_material))

    durability_type = form.get("durability_type")
    if durability_type:
        facts.append(AthleticPreferences(durability_type=durability_type))

    design_focus = form.get("design_focus")
    if design_focus:
        facts.append(DesignPreference(focus=design_focus))

    shape_type = form.get("shape_type")
    if shape_type:
        facts.append(ArtisticPreferences(shape_type=shape_type))

    color_family = form.get("color_family")
    if color_family:
        facts.append(ArtisticPreferences(color_family=color_family))

    detail_focus = form.get("detail_focus")
    if detail_focus:
        facts.append(ArtisticPreferences(detail_focus=detail_focus))

    return facts


def generate_recommendations(face_shape, face_width, user_facts):
    glasses_data = GlassesDataLoader(GLASSES_DATA_PATH).load_data()

    if not glasses_data:
        return []

    scoring_engine = SmartGlassesRecommendationSystem(glasses_data=glasses_data)
    scoring_engine.reset()

    scoring_engine.declare(FaceShape(shape=face_shape))
    scoring_engine.declare(FaceDimensions(face_width=face_width))

    for fact in user_facts:
        scoring_engine.declare(fact)

    scoring_engine.run()

    scoring_recommendations = [
        fact.as_dict()
        for _, fact in scoring_engine.facts.items()
        if isinstance(fact, FinalRecommendation)
    ]

    scoring_recommendations.sort(key=lambda item: item["score"], reverse=True)
    top_candidates = scoring_recommendations[:5]

    final_results = []

    for candidate in top_candidates:
        frame_data = candidate["frame_data"]

        confidence_engine = EnhancedGlassesKBS()
        confidence_engine.reset()

        confidence_engine.declare(FaceShape(shape=face_shape))
        confidence_engine.declare(FaceDimensions(face_width=face_width))
        confidence_engine.declare(UncertaintyEvidence(certainty=0.9))
        confidence_engine.declare(GlassFrame(**frame_data))

        for fact in user_facts:
            if isinstance(fact, UserPreferences):
                confidence_engine.declare(fact)

        confidence_engine.declare(State(status="confidence_analysis_start"))
        confidence_engine.run()

        confidence_engine.declare(State(status="confidence_analysis_complete"))
        confidence_engine.run()

        for _, fact in confidence_engine.facts.items():
            if isinstance(fact, FinalRecommendationWithCF):
                candidate["confidence_analysis"] = fact.as_dict()
                final_results.append(candidate)
                break

    final_results.sort(
        key=lambda item: item["confidence_analysis"]["overall_cf"],
        reverse=True
    )

    return final_results


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/questions", methods=["POST"])
def questions():
    try:
        path = request.form.get("path")
        gender = request.form.get("gender")

        image_path = save_uploaded_image()

        analyzer = FaceAnalyzer()
        face_analysis = analyzer.analyze_face(image_path)

        return render_template(
            "questions.html",
            path=path,
            gender=gender,
            face_shape=face_analysis["face_shape"],
            face_width=round(face_analysis["face_width"], 2),
        )

    except Exception as error:
        return render_template(
            "error.html",
            error_message=str(error),
            traceback=traceback.format_exc(),
        )


@app.route("/recommend", methods=["POST"])
def recommend():
    try:
        face_shape = request.form.get("face_shape", "Oval")
        face_width = float(request.form.get("face_width", 13.5))

        user_facts = build_user_facts(request.form)

        recommendations = generate_recommendations(
            face_shape=face_shape,
            face_width=face_width,
            user_facts=user_facts,
        )

        return render_template(
            "recommendations.html",
            recommendations=recommendations,
        )

    except Exception as error:
        return render_template(
            "error.html",
            error_message=str(error),
            traceback=traceback.format_exc(),
        )


if __name__ == "__main__":
    app.run(debug=True)