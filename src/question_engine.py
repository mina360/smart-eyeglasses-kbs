# question_engine.py
from experta import KnowledgeEngine, DefFacts, Rule, AS, MATCH, Fact
from facts import State, CurrentQuestion, PersonInfo, ProfessionalPreferences, \
                    AthleticPreferences, ArtisticPreferences, StylePreference, \
                    UserPreferences, ComfortIssue, DesignPreference, PathSelected, ActivityLevel 
class QuestionManagementEngine(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.questions_db = self._load_questions_data()
        self.user_answers = {}
        self.collected_facts = {}

    def _load_questions_data(self):
        return {
            "initial_path": {
                "text": "🌟 First, let's understand your primary use case:",
                "options": {
                    "1": "Professional/Work Environment",
                    "2": "Sports/Athletic Activities",
                    "3": "Fashion/Artistic Expression"
                },
                "on_answer_fact": "PathSelected",
                "on_answer_value_map": {
                    "1": {"path_type": "professional"},
                    "2": {"path_type": "athletic"},
                    "3": {"path_type": "artistic"}
                },
                "next_question_map": {
                    "1": "professional_priority_q",
                    "2": "athletic_activity_q",
                    "3": "artistic_design_focus_q"
                }
            },
            "gender_q": {
                "text": "👤 What is your gender?",
                "options": {"1": "Men", "2": "Women"},
                "on_answer_fact": "PersonInfo",
                "on_answer_value_map": {"1": {"gender": "men"}, "2": {"gender": "women"}},
                "next_question_id": None
            },
            "professional_priority_q": {
                "text": "🎯 What is your priority in your work environment?",
                "options": {"1": "Appearance that conveys confidence", "2": "Absolute comfort for long hours"},
                "on_answer_fact": "ProfessionalPreferences",
                "on_answer_value_map": {"1": {"professional_priority": "appearance"}, "2": {"professional_priority": "comfort"}},
                "next_question_map": {"1": "appearance_style_q", "2": "comfort_issue_q"}
            },
            "appearance_style_q": {
                "text": "✨ APPEARANCE FOCUS - What style do you prefer?",
                "options": {"1": "Classic and timeless", "2": "Modern and bold"},
                "on_answer_fact": "StylePreference",
                "on_answer_value_map": {"1": {"style": "classic_timeless"}, "2": {"style": "modern_bold"}},
                "next_question_id": "gender_q"
            },
            "comfort_issue_q": {
                "text": "😌 COMFORT FOCUS - What is your biggest source of discomfort?",
                "options": {"1": "Glasses slip down my nose", "2": "They're heavy and leave marks", "3": "They press on the sides of my head"},
                "on_answer_fact": "UserPreferences",
                "on_answer_value_map": {
                    "1": {"bridge_fit": "slips_down"},
                    "2": {"weight_pref": "lightweight"},
                    "3": {"bridge_fit": "sits_high"}
                },
                "next_question_id": "gender_q"
            },
            "athletic_activity_q": {
                "text": "⚡ What is your activity intensity level?",
                "options": {"1": "High (intense sports, running, cycling)", "2": "Medium/Low (casual sports, gym, walking)"},
                "on_answer_fact": "ActivityLevel",
                "on_answer_value_map": {"1": {"level": "high"}, "2": {"level": "medium_low"}},
                "next_question_map": {"1": "high_intensity_concern_q", "2": "medium_low_priority_q"}
            },
            "high_intensity_concern_q": {
                "text": "🔥 HIGH INTENSITY - What is your biggest concern?",
                "options": {"1": "Glasses might fall off (Stability)", "2": "Wind affects my vision"},
                "on_answer_fact": "AthleticPreferences",
                "on_answer_value_map": {"1": {"concern": "stability"}, "2": {"concern": "wind_vision"}},
                "next_question_map": {"1": "stability_design_q", "2": "gender_q"}
            },
            "stability_design_q": {
                "text": "🔒 STABILITY DESIGN - Which design for stability?",
                "options": {"1": "Wraps around the face", "2": "Rubber temples"},
                "on_answer_fact": "AthleticPreferences",
                "on_answer_value_map": {"1": {"stability_design": "wrap_around"}, "2": {"stability_design": "rubber_temples"}},
                "next_question_id": "gender_q"
            },
            "medium_low_priority_q": {
                "text": "💪 COMFORT/DURABILITY - What is most important?",
                "options": {"1": "Being very lightweight", "2": "Being durable enough"},
                "on_answer_fact": "UserPreferences",
                "on_answer_value_map": {"1": {"weight_pref": "lightweight"}, "2": {"durability_priority": "durable"}},
                "next_question_map": {"1": "material_for_lightness_q", "2": "durability_type_q"} # Added new question here
            },

            "material_for_lightness_q": {
                "text": "Which material do you prefer for lightness?",
                "options": {"1": "Lightweight plastic", "2": "Flexible metal"},
                "on_answer_fact": "UserPreferences",
                "on_answer_value_map": {"1": {"light_material": "lightweight_plastic"}, "2": {"light_material": "flexible_metal"}},
                "next_question_id": "gender_q"
            },
            "durability_type_q": {
                "text": "🛡️ DURABILITY TYPE - What kind of durability?",
                "options": {"1": "Flexible frame (bends without breaking)", "2": "Solid frame (impact resistant)"},
                "on_answer_fact": "AthleticPreferences",
                "on_answer_value_map": {"1": {"durability_type": "flexible"}, "2": {"durability_type": "solid"}},
                "next_question_id": "gender_q"
            },
            "artistic_design_focus_q": {
                "text": "🎨 ARTISTIC PATH - ✨ What attracts you first in design?",
                "options": {"1": "Design and shape", "2": "Color and pattern", "3": "Details"}, 
                "on_answer_fact": "DesignPreference",
                "on_answer_value_map": {"1": {"focus": "shape"}, "2": {"focus": "color"}, "3": {"focus": "details"}},
                "next_question_map": {"1": "artistic_shape_q", "2": "artistic_color_q", "3": "artistic_detail_focus_q"} 
            },
            "artistic_shape_q": {
                "text": "🔷 SHAPE FOCUS - What kind of shapes do you prefer?",
                "options": {"1": "Classic with a modern touch", "2": "Bold geometric", "3": "Oversized and eye-catching"},
                "on_answer_fact": "ArtisticPreferences",
                "on_answer_value_map": {"1": {"shape_type": "classic_modern"}, "2": {"shape_type": "geometric"}, "3": {"shape_type": "oversized"}},
                "next_question_id": "gender_q"
            },
            "artistic_color_q": {
                "text": "🌈 COLOR FOCUS - Which color family do you prefer?",
                "options": {"1": "Rich classics", "2": "Vibrant and bold", "3": "Transparent/crystal"},
                "on_answer_fact": "ArtisticPreferences",
                "on_answer_value_map": {"1": {"color_family": "rich_classic"}, "2": {"color_family": "vibrant_bold"}, "3": {"color_family": "transparent_crystal"}},
                "next_question_id": "gender_q"
            },
        
            "artistic_detail_focus_q": {
                "text": "🔍 DETAILS FOCUS - What kind of details do you prefer?",
                "options": {"1": "Simple and minimalist", "2": "Ornate and intricate"},
                "on_answer_fact": "ArtisticPreferences",
                "on_answer_value_map": {"1": {"detail_focus": "simple_minimalist"}, "2": {"detail_focus": "ornate_intricate"}},
                "next_question_id": "gender_q" 
            }
        }
        

    @DefFacts()
    def _initial_question_state(self):
        """Initializes the engine with the first question."""
        yield CurrentQuestion(id="initial_path", state="pending")

    @Rule(AS.cq << CurrentQuestion(id=MATCH.qid, state='pending'), salience=100)
    def ask_question(self, cq, qid):
        """Asks the current question, gets user input, and declares/modifies facts."""
        question_data = self.questions_db.get(qid)
        if not question_data:
            print(f"❌ Error: Question ID '{qid}' not found in database. Ending questioning.")
            self.retract(cq)
            self.declare(State(status='questions_ended'))
            return

        print(f"\n{question_data['text']}")
        for key, value in question_data['options'].items():
            print(f"{key}. {value}")

        answer = input("Your choice: ").strip().lower()

        mapped_answer = None
        if answer in question_data['options']:
            mapped_answer = answer
        else:
            for key, value in question_data['options'].items():
                if answer == value.lower():
                    mapped_answer = key 
                    break
        
        if mapped_answer is None:
            print("❌ Invalid choice. Please try again.")
            self.modify(cq, state='pending') 
            return

        self.user_answers[qid] = mapped_answer 
        self.modify(cq, state='answered')
        
        fact_to_declare_name = question_data.get('on_answer_fact')
        value_map = question_data.get('on_answer_value_map', {})

        if fact_to_declare_name and mapped_answer in value_map: 
            fact_data_to_declare = value_map[mapped_answer]
   
            fact_class = globals().get(fact_to_declare_name)
            
            if fact_class and issubclass(fact_class, Fact):
                existing_fact_obj = None
                for fid, fact_instance in self.facts.items():
                    if isinstance(fact_instance, fact_class):
                        existing_fact_obj = fact_instance
                        break

                if existing_fact_obj:
                    self.modify(existing_fact_obj, **fact_data_to_declare)
                    self.collected_facts[fact_to_declare_name] = existing_fact_obj
                    print(f"✅ Modified existing fact: {fact_to_declare_name}({fact_data_to_declare})")
                else:
                    new_fact = fact_class(**fact_data_to_declare)
                    self.declare(new_fact)
                    self.collected_facts[fact_to_declare_name] = new_fact
                    print(f"✅ Declared new fact: {fact_to_declare_name}({fact_data_to_declare})")
            else:
                print(f"⚠️ Warning: Fact class '{fact_to_declare_name}' not found or not a Fact type. Cannot declare.")
        
        next_q_id = None
        if question_data.get('next_question_map'):
            next_q_id = question_data['next_question_map'].get(mapped_answer) # Use mapped_answer
        elif question_data.get('next_question_id'):
            next_q_id = question_data['next_question_id']
        
        if next_q_id:
            self.declare(CurrentQuestion(id=next_q_id, state='pending'))
        else:
            self.declare(State(status='questions_ended'))
            print("\nAll preferences collected.")

    @Rule(AS.cq << CurrentQuestion(state='answered'), salience=50)
    def clean_answered_question(self, cq):
        """Retracts answered questions from the fact board."""
        self.retract(cq)

    def get_collected_facts(self):
        """Returns the facts collected during the questioning process."""
        return self.collected_facts