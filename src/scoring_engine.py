# scoring_engine.py
from experta import KnowledgeEngine, DefFacts, Rule, AS, MATCH, TEST, NOT
from facts import GlassFrame, FrameScore, PersonInfo, FaceShape, FaceDimensions, \
                    UserPreferences, StylePreference, AthleticPreferences, ArtisticPreferences, \
                    FinalRecommendation, PathSelected 
from glasses_loader import GlassesDataLoader 

class SmartGlassesRecommendationSystem(KnowledgeEngine):
    COMPATIBILITY_RULES = {
        'oblong': ['round', 'aviator', 'square'],
        'square': ['round', 'oval', 'aviator', 'cat-eye'],
        'round': ['square', 'rectangle', 'geometric'],
        'oval': ['square', 'rectangle', 'round', 'aviator', 'cat-eye', 'geometric'],
        'heart': ['aviator', 'round', 'cat-eye'],
        'triangle': ['cat-eye', 'square', 'rectangle'],
        'diamond': ['cat-eye', 'oval', 'round'],
        'undefined': ['square', 'rectangle', 'aviator']
    }

    def __init__(self, glasses_data): 
        super().__init__()
        self.glasses_db = glasses_data
        self.frame_scores = {}
        self.reasoning_chain = []

    def _update_score(self, fs, fid, points, reason):
        current_reasons = list(fs['reasons'])
        if reason not in current_reasons:
            new_score = fs['score'] + points
            new_reasons = current_reasons + [reason]
            self.modify(fs, score=new_score, reasons=new_reasons)
            self.frame_scores[fid] = {'score': new_score, 'reasons': new_reasons}
            self.reasoning_chain.append(f"Added {points} to {fid} for {reason}")

    @DefFacts()
    def _initial_facts(self):
        for glass in self.glasses_db:
            yield GlassFrame(**glass)
        
    @Rule(AS.gf << GlassFrame(frame_id=MATCH.fid), NOT(FrameScore(frame_id=MATCH.fid)), salience=1000)
    def initialize_frame_base_score(self, fid):
        self.declare(FrameScore(frame_id=fid, score=0, reasons=[]))
        self.frame_scores[fid] = {'score': 0, 'reasons': []}

    @Rule(PersonInfo(gender=MATCH.user_gender), 
          GlassFrame(frame_id=MATCH.fid, gender=MATCH.user_gender),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          salience=900)
    def add_gender_score(self, fs, fid):
        self._update_score(fs, fid, 10, "Gender Match")

    @staticmethod
    def _is_shape_compatible(user_shape, glass_shape):
        return glass_shape in SmartGlassesRecommendationSystem.COMPATIBILITY_RULES.get(user_shape, [])

    @Rule(FaceShape(shape=MATCH.user_shape), 
          GlassFrame(frame_id=MATCH.fid, shape=MATCH.glass_shape),
          AS.fs << FrameScore(frame_id=MATCH.fid),
          TEST(lambda user_shape, glass_shape: SmartGlassesRecommendationSystem._is_shape_compatible(user_shape, glass_shape)),
          salience=880)
    def add_shape_score(self, fs, fid, user_shape, glass_shape):
        self._update_score(fs, fid, 15, "Shape Match")

    @staticmethod
    def _is_size_compatible(user_face_width, glass_size):
        size_ranges = {'small': (10.0, 13.0), 'medium': (13.0, 15.0), 'large': (15.0, 17.0), 'extra large': (17.0, 20.0)}
        min_w, max_w = size_ranges.get(str(glass_size).lower().strip(), (0, 0))
        return min_w <= user_face_width <= max_w
    
    @Rule(FaceDimensions(face_width=MATCH.user_face_width),
          GlassFrame(frame_id=MATCH.fid, size=MATCH.glass_size),
          AS.fs << FrameScore(frame_id=MATCH.fid),
          TEST(lambda user_face_width, glass_size: SmartGlassesRecommendationSystem._is_size_compatible(user_face_width, glass_size)),
          salience=860)
    def add_size_score(self, fs, fid, user_face_width, glass_size):
        self._update_score(fs, fid, 15, "Size Match")

    @Rule(UserPreferences(weight_pref='lightweight'), 
          GlassFrame(frame_id=MATCH.fid, weight=MATCH.w),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda w: w is not None and w <= 15), 
          salience=800)
    def add_lightweight_score(self, fs, fid):
        self._update_score(fs, fid, 15, "Lightweight")


    @Rule(UserPreferences(light_material='lightweight_plastic'),
          GlassFrame(frame_id=MATCH.fid, material='plastic'),
          AS.fs << FrameScore(frame_id=MATCH.fid),
          salience=795)
    def add_lightweight_plastic_score(self, fs, fid):
        self._update_score(fs, fid, 10, "Preferred lightweight plastic material")

    @Rule(UserPreferences(light_material='flexible_metal'),
          GlassFrame(frame_id=MATCH.fid, material=MATCH.mat),
          AS.fs << FrameScore(frame_id=MATCH.fid),
          TEST(lambda mat: mat in ['titanium', 'flex-metal', 'stainless steel']),
          salience=795)
    def add_flexible_metal_score(self, fs, fid):
        self._update_score(fs, fid, 10, "Preferred flexible metal material")

    @Rule(UserPreferences(bridge_fit='slips_down'), 
          GlassFrame(frame_id=MATCH.fid, bridge=MATCH.b),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda b: b is not None and 15 <= b <= 18), 
          salience=790)
    def add_bridge_fit_score_narrow(self, fs, fid):
        self._update_score(fs, fid, 15, "Bridge Fit for Slipping")
        
    @Rule(UserPreferences(bridge_fit='sits_high'), 
          GlassFrame(frame_id=MATCH.fid, bridge=MATCH.b),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda b: b is not None and b >= 21), 
          salience=780)
    def add_bridge_fit_score_wide(self, fs, fid):
        self._update_score(fs, fid, 15, "Wide Bridge for Comfort")

    @Rule(StylePreference(style='classic_timeless'), 
          GlassFrame(frame_id=MATCH.fid, features=MATCH.f),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda f: 'classic_timeless' in f or 'classic' in f), 
          salience=750)
    def add_classic_style_score(self, fs, fid):
        self._update_score(fs, fid, 10, "Classic Style")
        
    @Rule(StylePreference(style='modern_bold'), 
          GlassFrame(frame_id=MATCH.fid, features=MATCH.f),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda f: 'modern_bold' in f or 'modern' in f), 
          salience=750)
    def add_modern_style_score(self, fs, fid):
        self._update_score(fs, fid, 10, "Modern Style")

    @Rule(AthleticPreferences(stability_design=MATCH.design), 
          GlassFrame(frame_id=MATCH.fid, features=MATCH.f),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda design, f: design in f), 
          salience=700)
    def add_stability_design_score(self, fs, fid, design):
        self._update_score(fs, fid, 15, f"Stability: {design}")

    @Rule(AthleticPreferences(durability_type=MATCH.dtype), 
          GlassFrame(frame_id=MATCH.fid, features=MATCH.f),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda dtype, f: dtype in f), 
          salience=690)
    def add_durability_score(self, fs, fid, dtype):
        self._update_score(fs, fid, 12, f"Durability: {dtype}")

    @Rule(AthleticPreferences(concern='wind_vision'), 
          GlassFrame(frame_id=MATCH.fid, features=MATCH.f),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda f: 'wind_vision' in f or 'wrap_around' in f), 
          salience=680)
    def add_wind_protection_score(self, fs, fid):
        self._update_score(fs, fid, 15, "Wind Protection")

    @Rule(ArtisticPreferences(shape_type=MATCH.stype), 
          GlassFrame(frame_id=MATCH.fid, features=MATCH.f),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda stype, f: stype in f), 
          salience=650)
    def add_artistic_shape_score(self, fs, fid, stype):
        self._update_score(fs, fid, 15, f"Artistic Shape: {stype}")

    @Rule(ArtisticPreferences(color_family=MATCH.color), 
          GlassFrame(frame_id=MATCH.fid, features=MATCH.f),
          AS.fs << FrameScore(frame_id=MATCH.fid), 
          TEST(lambda color, f: color in f), 
          salience=640)
    def add_artistic_color_score(self, fs, fid, color):
        self._update_score(fs, fid, 12, f"Color Preference: {color}")

    @Rule(ArtisticPreferences(detail_focus='simple_minimalist'),
          GlassFrame(frame_id=MATCH.fid, design_details=MATCH.dd),
          AS.fs << FrameScore(frame_id=MATCH.fid),
          TEST(lambda dd: 'minimalist' in dd or 'simple' in dd),
          salience=630)
    def add_artistic_detail_simple_score(self, fs, fid):
        self._update_score(fs, fid, 15, "Artistic Detail: Simple/Minimalist")

    @Rule(ArtisticPreferences(detail_focus='ornate_intricate'),
          GlassFrame(frame_id=MATCH.fid, design_details=MATCH.dd),
          AS.fs << FrameScore(frame_id=MATCH.fid),
          TEST(lambda dd: 'ornate' in dd or 'intricate' in dd),
          salience=630)
    def add_artistic_detail_ornate_score(self, fs, fid):
        self._update_score(fs, fid, 15, "Artistic Detail: Ornate/Intricate")

    @Rule(AS.fs << FrameScore(frame_id=MATCH.fid, score=MATCH.s, reasons=MATCH.r),
          AS.gf << GlassFrame(frame_id=MATCH.fid),
          TEST(lambda s, r: s >= 20 and len(r) >= 2),
          NOT(FinalRecommendation(frame_id=MATCH.fid)),
          salience=-100)
    def collect_high_score_recommendations(self, fs, fid, s, r, gf):
        self.declare(FinalRecommendation(frame_id=fid, score=s, reasons=r, frame_data=gf.as_dict()))