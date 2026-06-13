# confidence_engine.py

from experta import *
from facts import State, GlassFrame, FaceShape, FaceDimensions, UserPreferences, \
    ConfidenceFactor, UncertaintyEvidence, FinalRecommendationWithCF, AggregationData
import collections
import collections.abc
import sys


if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    collections.Mapping = collections.abc.Mapping
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Iterable = collections.abc.Iterable
    collections.Iterator = collections.abc.Iterator
    collections.KeysView = collections.abc.KeysView
    collections.ValuesView = collections.abc.ValuesView

class UncertaintyManager:
    """إدارة عمليات دمج عوامل الثقة وتصنيف المخاطر."""
    @staticmethod
    def combine_cf(cf1, cf2):
        """تدمج عاملين للثقة."""
        if cf1 is None: return cf2
        if cf2 is None: return cf1
        if cf1 >= 0 and cf2 >= 0: return cf1 + cf2 - (cf1 * cf2)
        elif cf1 < 0 and cf2 < 0: return cf1 + cf2 + (cf1 * cf2)
        else: return (cf1 + cf2) / (1 - min(abs(cf1), abs(cf2)))

    @staticmethod
    def categorize_risk(cf_value):
        """تصنيف مستوى المخاطر بناءً على عامل الثقة."""
        if cf_value >= 0.8: return "low"
        elif cf_value >= 0.5: return "medium"
        else: return "high"

class EnhancedGlassesKBS(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.uncertainty_manager = UncertaintyManager()
        self.compatibility_matrix = {
            'oblong': {'round': 0.9, 'aviator': 0.85, 'square': 0.8},
            'square': {'round': 0.9, 'oval': 0.8, 'cat-eye': 0.75}, 
            'round': {'square': 0.9, 'rectangle': 0.85, 'geometric': 0.8},
            'oval': {'all': 0.95},
            'heart': {'aviator': 0.9, 'round': 0.85, 'cat-eye': 0.8},
            'triangle': {'cat-eye': 0.9, 'square': 0.85, 'rectangle': 0.8},
            'diamond': {'cat-eye': 0.9, 'oval': 0.85, 'round': 0.8},
            'undefined': {'square': 0.7, 'rectangle': 0.7, 'aviator': 0.7}
        }
        self.weights = {'shape': 0.5, 'size': 0.3, 'comfort': 0.2}

  

    @Rule(FaceShape(shape=MATCH.face_shape),
          UncertaintyEvidence(certainty=MATCH.detection_cf),
          GlassFrame(frame_id=MATCH.fid, shape=MATCH.glass_shape),
          salience=100)
    def analyze_face_shape(self, face_shape, detection_cf, fid, glass_shape):
        """تحليل عامل الثقة لتوافق شكل الوجه مع شكل النظارة."""
        
        compatible_shapes_for_face = self.compatibility_matrix.get(str(face_shape).lower(), {})
        
       
        base_cf = compatible_shapes_for_face.get(str(glass_shape).lower(), 
                                                compatible_shapes_for_face.get('all', 0.1))

        final_cf = self.uncertainty_manager.combine_cf(base_cf, detection_cf)
        self.declare(ConfidenceFactor(frame_id=fid, category="shape", cf_value=final_cf))

    @Rule(FaceDimensions(face_width=MATCH.face_width),
          GlassFrame(frame_id=MATCH.fid, frame_width=MATCH.frame_width),
          TEST(lambda face_width, frame_width: 
               face_width is not None and frame_width is not None and face_width > 0 and frame_width > 0),
          salience=90)
    def analyze_size(self, face_width, fid, frame_width):
        """تحليل عامل الثقة لتوافق حجم الإطار مع عرض الوجه."""
        ratio = (frame_width / 10) / face_width
        size_cf = max(0.0, 1 - abs(1.05 - ratio) * 5) # تم الحفاظ على نفس الصيغة الحسابية الأصلية
        self.declare(ConfidenceFactor(frame_id=fid, category="size", cf_value=size_cf))

    @Rule(UserPreferences(bridge_fit='slips_down'),
          GlassFrame(frame_id=MATCH.fid, bridge_width=MATCH.bridge_width),
          TEST(lambda bridge_width: bridge_width is not None and 15 <= bridge_width <= 18),
          salience=80)
    def analyze_comfort_high(self, fid):
        """تحديد عامل ثقة مرتفع للراحة لجسر الأنف المناسب."""
        self.declare(ConfidenceFactor(frame_id=fid, category="comfort", cf_value=0.9))

    @Rule(UserPreferences(bridge_fit='slips_down'),
          GlassFrame(frame_id=MATCH.fid, bridge_width=MATCH.bridge_width),
          NOT(ConfidenceFactor(frame_id=MATCH.fid, category="comfort", cf_value=0.9)), 
          TEST(lambda bridge_width: bridge_width is not None and 13 <= bridge_width <= 20),
          salience=79)
    def analyze_comfort_medium(self, fid):
        """تحديد عامل ثقة متوسط للراحة لجسر الأنف الأقل مثالية."""
        self.declare(ConfidenceFactor(frame_id=fid, category="comfort", cf_value=0.7))

    @Rule(UserPreferences(bridge_fit='slips_down'),
          GlassFrame(frame_id=MATCH.fid, bridge_width=MATCH.bridge_width), 
          
          NOT(ConfidenceFactor(frame_id=MATCH.fid, category="comfort")), 
         
          TEST(lambda bridge_width: bridge_width is None or bridge_width < 13 or bridge_width > 20),
          salience=78) 
    def analyze_comfort_low_default(self, fid, bridge_width):
        """تحديد عامل ثقة منخفض للراحة كقيمة افتراضية إذا لم تنطبق الشروط الأخرى."""
        self.declare(ConfidenceFactor(frame_id=fid, category="comfort", cf_value=0.4))

   
    @Rule(State(status='confidence_analysis_start'),
          AS.gf << GlassFrame(frame_id=MATCH.fid),
          NOT(AggregationData(frame_id=MATCH.fid)), 
          salience=70)
    def initialize_aggregation(self, fid):
        """تهيئة حقيقة AggregationData لكل إطار قيد التحليل."""
        self.declare(AggregationData(frame_id=fid, weighted_sum=0.0, total_weight=0.0, confidence_breakdown={}))


    @Rule(AS.ad << AggregationData(frame_id=MATCH.fid, weighted_sum=MATCH.ws, total_weight=MATCH.tw, confidence_breakdown=MATCH.cbd),
          AS.cf << ConfidenceFactor(frame_id=MATCH.fid, category='shape', cf_value=MATCH.cf_val),
          salience=60)
    def aggregate_shape_factor(self, ad, cf, ws, tw, cbd, cf_val):
        """تجميع عامل الثقة الخاص بالشكل."""
        new_ws = ws + (cf_val * self.weights['shape'])
        new_tw = tw + self.weights['shape']
        new_cbd = dict(cbd)
        new_cbd['shape'] = cf_val 
        self.modify(ad, weighted_sum=new_ws, total_weight=new_tw, confidence_breakdown=new_cbd)
        self.retract(cf) 
        
    @Rule(AS.ad << AggregationData(frame_id=MATCH.fid, weighted_sum=MATCH.ws, total_weight=MATCH.tw, confidence_breakdown=MATCH.cbd),
          AS.cf << ConfidenceFactor(frame_id=MATCH.fid, category='size', cf_value=MATCH.cf_val),
          salience=59)
    def aggregate_size_factor(self, ad, cf, ws, tw, cbd, cf_val):
        """تجميع عامل الثقة الخاص بالحجم."""
        new_ws = ws + (cf_val * self.weights['size'])
        new_tw = tw + self.weights['size']
        new_cbd = dict(cbd)
        new_cbd['size'] = cf_val
        self.modify(ad, weighted_sum=new_ws, total_weight=new_tw, confidence_breakdown=new_cbd)
        self.retract(cf)

   
    @Rule(AS.ad << AggregationData(frame_id=MATCH.fid, weighted_sum=MATCH.ws, total_weight=MATCH.tw, confidence_breakdown=MATCH.cbd),
          AS.cf << ConfidenceFactor(frame_id=MATCH.fid, category='comfort', cf_value=MATCH.cf_val),
          salience=58)
    def aggregate_comfort_factor(self, ad, cf, ws, tw, cbd, cf_val):
        """تجميع عامل الثقة الخاص بالراحة."""
        new_ws = ws + (cf_val * self.weights['comfort'])
        new_tw = tw + self.weights['comfort']
        new_cbd = dict(cbd)
        new_cbd['comfort'] = cf_val
        self.modify(ad, weighted_sum=new_ws, total_weight=new_tw, confidence_breakdown=new_cbd)
        self.retract(cf)

   
    
    @Rule(State(status='confidence_analysis_complete'), 
          AS.ad << AggregationData(frame_id=MATCH.fid, weighted_sum=MATCH.ws, total_weight=MATCH.tw, confidence_breakdown=MATCH.cbd),
          TEST(lambda tw: tw > 0), 
          NOT(FinalRecommendationWithCF(frame_id=MATCH.fid)), 
          salience=-100)
    
    def finalize_recommendation(self, ad, fid, ws, tw, cbd):
        """حساب عامل الثقة الإجمالي وإعلان التوصية النهائية بالثقة."""
        final_cf = ws / tw
        
        self.declare(FinalRecommendationWithCF(
            frame_id=fid, 
            overall_cf=final_cf,
            confidence_breakdown=cbd, 
            risk_level=self.uncertainty_manager.categorize_risk(final_cf)
        ))
        self.retract(ad)