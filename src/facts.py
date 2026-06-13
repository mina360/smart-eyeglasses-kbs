# facts.py
from experta import Fact, Field

class State(Fact): pass

class PersonInfo(Fact): pass
class FaceShape(Fact): pass
class FaceDimensions(Fact): pass
class UserPreferences(Fact): pass
class UserPath(Fact): pass
class ProfessionalPreferences(Fact): pass
class AthleticPreferences(Fact): pass
class ArtisticPreferences(Fact): pass
class StylePreference(Fact): pass
class ComfortIssue(Fact): pass
class ActivityLevel(Fact): pass
class DesignPreference(Fact): pass

class Question(Fact):
    id = Field(str, mandatory=True)
    text = Field(str, mandatory=True)
    options = Field(dict, mandatory=True)
    on_answer_fact = Field(str, default=None)
    on_answer_value_map = Field(dict, default=None)
    next_question_id = Field(str, default=None)
    next_question_map = Field(dict, default=None)

class CurrentQuestion(Fact):
    id = Field(str, mandatory=True)
    state = Field(str, default='pending')

class UserAnswer(Fact):
    question_id = Field(str, mandatory=True)
    answer_choice = Field(str, mandatory=True)

class PathSelected(Fact):
    path_type = Field(str, mandatory=True)

class GlassFrame(Fact):
    frame_id = Field(str, mandatory=True)
    shape = Field(str, default='n/a')
    material = Field(str, default='n/a')
    size = Field(str, default='n/a')
    gender = Field(str, default='n/a')
    weight = Field(float, default=0.0)
    bridge = Field(float, default=0.0)
    bridge_width = Field(float, default=0.0)
    frame_width = Field(float, default=0.0)
    rim = Field(str, default='n/a')
    color = Field(str, default='n/a')
    features = Field(list, default=[])

class FrameScore(Fact):
    frame_id = Field(str, mandatory=True)
    score = Field(int, default=0)
    reasons = Field(list, default=[])

class FinalRecommendation(Fact):
    frame_id = Field(str)
    score = Field(int)
    reasons = Field(list)
    frame_data = Field(dict)

class ConfidenceFactor(Fact):
    frame_id = Field(str, mandatory=True)
    category = Field(str, mandatory=True)
    cf_value = Field(float, default=0.0)

class UncertaintyEvidence(Fact):
    certainty = Field(float, default=1.0)

class FinalRecommendationWithCF(Fact):
    frame_id = Field(str)
    overall_cf = Field(float)
    confidence_breakdown = Field(dict)
    risk_level = Field(str)

class AggregationData(Fact):
    frame_id = Field(str)
    weighted_sum = Field(float, default=0.0)
    total_weight = Field(float, default=0.0)
    confidence_breakdown = Field(dict, default=lambda: {})