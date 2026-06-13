# app.py
import traceback

from config import GLASSES_DATA_PATH, IMAGE_PATH
from face_analyzer import FaceAnalyzer
from glasses_loader import GlassesDataLoader
from question_engine import QuestionManagementEngine
from scoring_engine import SmartGlassesRecommendationSystem
from confidence_engine import EnhancedGlassesKBS, UncertaintyManager


from experta import Fact
from facts import State, PersonInfo, FaceShape, FaceDimensions, UserPreferences, \
                    ProfessionalPreferences, AthleticPreferences, ArtisticPreferences, \
                    StylePreference, ComfortIssue, DesignPreference, \
                    GlassFrame, FinalRecommendation, UncertaintyEvidence, FinalRecommendationWithCF


class SmartGlassesRecommender:
    def __init__(self, glasses_data_path, image_path):
        self.glasses_data_path = glasses_data_path
        self.image_path = image_path
        self.face_analyzer = FaceAnalyzer()
        self.glasses_data_loader = GlassesDataLoader(self.glasses_data_path)

    def run_recommendation(self):
        try:
            print("🔍 Analyzing image...")
            face_analysis = self.face_analyzer.analyze_face(self.image_path)
            print(f"✅ Face Analysis: Shape={face_analysis['face_shape']}, Width={face_analysis['face_width']:.2f}cm")

            print("\n" + "="*50 + "\nSTAGE 0: Dynamic Questioning\n" + "="*50)
            question_engine = QuestionManagementEngine()
            question_engine.reset()
            question_engine.run() 

            collected_user_facts = question_engine.get_collected_facts()
            
            glasses_data = self.glasses_data_loader.load_data()
            if not glasses_data:
                print("Exiting due to failure in loading glasses data.")
                return

            print("\n" + "="*50 + "\nSTAGE 1: Scoring Engine - Finding Top Candidates\n" + "="*50)
            scoring_engine = SmartGlassesRecommendationSystem(glasses_data=glasses_data) 
            scoring_engine.reset()
            
           
            scoring_engine.declare(FaceShape(shape=face_analysis.get('face_shape')))
            scoring_engine.declare(FaceDimensions(face_width=face_analysis.get('face_width')))
            
          
            for fact_name, fact_obj in collected_user_facts.items():
               
                if isinstance(fact_obj, Fact):
                    
                    fact_class = globals().get(fact_name) 
                    if fact_class and issubclass(fact_class, Fact):
                        
                        scoring_engine.declare(fact_class(**fact_obj.as_dict()))
                    else:
                        print(f"⚠️ Warning: Could not re-declare {fact_name} in scoring engine (class not found or not a Fact type).")
                else:
                    print(f"⚠️ Warning: Collected item '{fact_name}' is not an experta.Fact instance. Skipping.")
            
            print("\n🤖 Running Scoring Engine...")
            scoring_engine.run()
            
            scoring_recs = [f.as_dict() for f_id, f in scoring_engine.facts.items() if isinstance(f, FinalRecommendation)]
            scoring_recs.sort(key=lambda x: x['score'], reverse=True)
            top_candidates = scoring_recs[:5]

            if not top_candidates:
                print("\n❌ No suitable candidates found after scoring.")
                return
            print(f"\n✅ Found {len(top_candidates)} top candidates from scoring engine.")

            print("\n" + "="*50 + "\nSTAGE 2: Confidence Engine - Deep Analysis\n" + "="*50)
            confidence_engine = EnhancedGlassesKBS()
            final_results = []

            for candidate in top_candidates:
                frame_data = candidate['frame_data']
                frame_id = str(frame_data.get('frame_id'))
                print(f"\nAnalyzing candidate: {frame_id} (Score: {candidate['score']})")
                
                confidence_engine.reset()
                
                confidence_engine.declare(FaceShape(shape=face_analysis['face_shape']))
                confidence_engine.declare(FaceDimensions(face_width=face_analysis['face_width']))
                confidence_engine.declare(UncertaintyEvidence(certainty=0.9))
                confidence_engine.declare(GlassFrame(**frame_data))
                
              
                user_prefs_fact_from_q = collected_user_facts.get('UserPreferences')
                if isinstance(user_prefs_fact_from_q, UserPreferences): 
                    confidence_engine.declare(UserPreferences(**user_prefs_fact_from_q.as_dict()))

                confidence_engine.declare(State(status='confidence_analysis_start'))
                
                confidence_engine.run()
                
                confidence_engine.declare(State(status='confidence_analysis_complete'))
                confidence_engine.run()

                confidence_result_found = False
                for _, f in confidence_engine.facts.items():
                    if isinstance(f, FinalRecommendationWithCF):
                        candidate['confidence_analysis'] = f.as_dict()
                        final_results.append(candidate)
                        confidence_result_found = True
                        break
                
                if not confidence_result_found:
                    print(f"    -> ⚠️ No confidence analysis result for Frame {frame_id}. Skipping.")
            
            print("\n" + "="*60 + "\n🏆 FINAL HYBRID RECOMMENDATIONS 🏆\n" + "="*60)
            if not final_results:
                print("\n❌ No recommendations passed the confidence analysis.")
            else:
                final_results.sort(key=lambda x: x['confidence_analysis']['overall_cf'], reverse=True)
                for i, rec in enumerate(final_results, 1):
                    score_data, cf_data = rec, rec['confidence_analysis']
                    frame_data = rec['frame_data']
                    print(f"\n{i}. Frame ID: {rec['frame_id']}")
                    print(f"    - Score: {score_data['score']} | 🌟 Confidence: {cf_data['overall_cf']:.1%} | Risk: {cf_data['risk_level'].upper()}")
                    print(f"    - Shape: {frame_data.get('shape', 'N/A')}, Material: {frame_data.get('material', 'N/A')}")
                    print(f"    - Reasons: {', '.join(score_data['reasons'])}")
                    print(f"    - Breakdown: Shape(CF:{cf_data['confidence_breakdown'].get('shape', 0.0):.2f}) | Size(CF:{cf_data['confidence_breakdown'].get('size', 0.0):.2f}) | Comfort(CF:{cf_data['confidence_breakdown'].get('comfort', 0.0):.2f})")

        except Exception as e:
            print(f"\n❌ An unexpected error occurred: {e}")
            traceback.print_exc()
            print("\nPlease make sure you have:")
            print("    - A valid image file at 'image.png' (or update IMAGE_PATH)")
            print("    - The glasses database at 'glasses_cleaned_augmented_filled.xlsx' (or update GLASSES_DATA_PATH)")
            print("    - All required libraries installed (opencv-python, mediapipe, pandas, experta)")

if __name__ == "__main__":
    recommender = SmartGlassesRecommender(GLASSES_DATA_PATH, IMAGE_PATH)
    recommender.run_recommendation()