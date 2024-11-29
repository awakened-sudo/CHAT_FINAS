# app.py
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import Dict
import random

# Load environment variables
load_dotenv()

class AssistantUI:
    def __init__(self):
        # Load and validate OpenAI API key
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables. Please ensure your .env file contains this key.")
        
        # Initialize OpenAI client with API key from .env
        self.client = OpenAI(api_key=api_key)
        
        # Hardcoded assistant and vector store IDs
        self.ASSISTANT_ID = "asst_Qmoz7GL0UQRGnTpSvHUh1jrE"
        self.VECTOR_STORE_ID = "vs_SbBbS2hVY0NMwpAp3IYHASpb"
        
        # Dictionary to store assistant names and IDs
        self.assistants = {
            "BARONIA_B": "asst_Qmoz7GL0UQRGnTpSvHUh1jrE",
            "FACE_OF_MALAYSIA": "asst_tzadLKlr6MmeXffh2n1yWZuX", 
            "MENJUNJUNG_KASIH": "asst_xxf55F2JbdteRsGw5m46FzUC", 
        }

        # Add translations dictionary
        self.translations = {
            "English": {
                "placeholder": "Ask your question about FINAS content...",
                "ask_button": "Ask",
                "creative_button": "I'm Feeling Creative",
                "suggested_questions": "Suggested Questions",
                "suggestions": [
                    "Show me the scene where the protagonist meets the antagonist?",
                    "Which scene has a sad moment?",
                    "What are the summary of the video?",
                    "Which scene is at the midpoint of the movie?"
                ],
                "processing": "Processing your query...",
                "select_assistant": "Select Assistant",
                "start_new_conversation": "Start New Conversation"
            },
            "Bahasa Melayu": {
                "placeholder": "Tanya soalan anda tentang kandungan FINAS...",
                "ask_button": "Tanya",
                "creative_button": "Rasa Kreatif",
                "suggested_questions": "Soalan Dicadangkan",
                "suggestions": [
                    "Tunjukkan babak di mana protagonis bertemu antagonis?",
                    "Babak manakah yang mempunyai momen sedih?",
                    "Apakah ringkasan video ini?",
                    "Babak manakah yang berada di pertengahan filem?"
                ],
                "processing": "Memproses pertanyaan anda...",
                "select_assistant": "Pilih Pembantu",
                "start_new_conversation": "Mulakan Perbualan Baru"
            },
            "عربي": {  
                "placeholder": "...اطرح سؤالك حول محتوى فيناس",
                "ask_button": "اسأل",
                "creative_button": "أشعر بالإبداع",
                "suggested_questions": "الأسئلة المقترحة",
                "suggestions": [
                    "أرني المشهد حيث يلتقي البطل مع الخصم؟",
                    "أي مشهد فيه لحظة حزينة؟",
                    "ما هو ملخص الفيديو؟",
                    "أي مشهد في منتصف الفيلم؟"
                ],
                "processing": "...جاري معالجة استفسارك",
                "select_assistant": "اختر مساعد",
                "start_new_conversation": "ابدأ محادثة جديدة"
            },
            "中文": {
                "placeholder": "询问有关FINAS内容的问题...",
                "ask_button": "询问",
                "creative_button": "创意灵感",
                "suggested_questions": "建议问题",
                "suggestions": [
                    "显示主角与反派相遇的场景？",
                    "哪个场景有悲伤的时刻？",
                    "视频的摘要是什么？",
                    "哪个场景在电影的中点？"
                ],
                "processing": "正在处理您的查询...",
                "select_assistant": "选择助手",
                "start_new_conversation": "开始新对话"
            },
            "தமிழ்": {
                "placeholder": "FINAS உள்ளடக்கம் பற்றி கேள்வி கேளுங்கள்...",
                "ask_button": "கேள்",
                "creative_button": "படைப்பாற்றல் உணர்கிறேன்",
                "suggested_questions": "பரிந்துரைக்கப்பட்ட கேள்விகள்",
                "suggestions": [
                    "நாயகன் எதிரியை சந்திக்கும் காட்சியைக் காட்டுங்கள்?",
                    "எந்த காட்சியில் சோகமான தருணம் உள்ளது?",
                    "வீடியோவின் சுருக்கம் என்ன?",
                    "எந்த காட்சி படத்தின் நடுப்பகுதியில் உள்ளது?"
                ],
                "processing": "உங்கள் கேள்வியை செயலாக்குகிறது...",
                "select_assistant": "உதவியாளரை தேர்ந்தெடுக்கவும்",
                "start_new_conversation": "புதிய உரையாடலை தொடங்கவும்"
            }
        }

        # Add session state initialization
        if 'thread_id' not in st.session_state:
            st.session_state.thread_id = None
        if 'conversation_active' not in st.session_state:
            st.session_state.conversation_active = False

    def get_text(self, key: str, language: str) -> str:
        """Get translated text for the given key and language"""
        return self.translations[language][key]

    def get_creative_prompt(self, selected_language: str) -> str:
        """Generate creative prompts focused on video analysis and scene understanding"""
        creative_prompts = {
            "English": [
                "Analyze the emotional journey of characters throughout this scene",
                "Identify key visual storytelling techniques used in this segment",
                "Examine the scene transitions and their impact on storytelling",
                "Explore how lighting and color are used to convey mood in this scene",
                "Break down the camera movements and their narrative significance",
                "Analyze the pacing and rhythm of dialogue and action",
                "Identify symbolism and visual metaphors in this sequence",
                "Examine character dynamics and relationships in this scene"
            ],
            "Bahasa Melayu": [
                "Analisis perjalanan emosi watak dalam babak ini",
                "Kenalpasti teknik penceritaan visual dalam segmen ini",
                "Teliti peralihan babak dan kesannya terhadap penceritaan",
                "Terokai penggunaan pencahayaan dan warna untuk menyampaikan suasana",
                "Huraikan pergerakan kamera dan kepentingannya dalam naratif",
                "Analisis tempo dan ritma dialog serta aksi",
                "Kenalpasti simbolisme dan metafora visual dalam urutan ini",
                "Teliti dinamik dan hubungan antara watak dalam babak ini"
            ],
            "عربي": [
                "تحليل الرحلة العاطفية للشخصيات في هذا المشهد",
                "تحديد تقنيات السرد البصري في هذا المقطع",
                "دراسة انتقالات المشهد وتأثيرها على السرد",
                "استكشاف استخدام الإضاءة واللون لنقل المزاج",
                "تحليل حركات الكاميرا وأهميتها السردية",
                "تحليل وتيرة وإيقاع الحوار والعمل",
                "تحديد الرمزية والاستعارات البصرية في هذا التسلسل",
                "دراسة ديناميكيات وعلاقات الشخصيات في هذا المشهد"
            ],
            "中文": [
                "分析这个场景中人物的情感变化",
                "识别此片段中使用的视觉叙事技巧",
                "研究场景转换及其对故事叙述的影响",
                "探索光线和色彩如何传达情绪",
                "分析摄像机运动及其叙事意义",
                "分析对话和动作的节奏感",
                "识别此序列中的象征主义和视觉隐喻",
                "研究这个场景中的角色互动和关系"
            ],
            "தமிழ்": [
                "இந்த காட்சியில் கதாபாத்திரங்களின் உணர்ச்சி பயணத்தை பகுப்பாய்வு செய்க",
                "இந்த பகுதியில் பயன்படுத்தப்படும் விஷுவல் கதை சொல்லும் நுட்பங்களை கண்டறியவும்",
                "காட்சி மாற்றங்களையும் கதை சொல்லலில் அவற்றின் தாக்கத்தையும் ஆராயுங்கள்",
                "மனநிலையை வெளிப்படுத்த ஒளி மற்றும் வண்ணம் பயன்படுத்தப்படும் விதத்தை ஆராயுங்கள்",
                "கேமரா அசைவுகள் மற்றும் அவற்றின் விவரிப்பு முக்கியத்துவத்தை பகுப்பாய்வு செய்யவும்",
                "உரையாடல் மற்றும் செயலின் வேகம் மற்றும் ரித்தத்தை பகுப்பாய்வு செய்யவும்",
                "இந்த வரிசையில் உள்ள சின்னங்கள் மற்றும் காட்சி உருவகங்களை கண்டறியவும்",
                "இந்த காட்சியில் கதாபாத்திர இயக்கவியல் மற்றும் உறவுகளை ஆராயவும்"
            ]
        }
            
        return random.choice(creative_prompts[selected_language])

    def create_or_get_thread(self):
        """Create a new thread if none exists or return existing thread ID"""
        if not st.session_state.thread_id:
            thread = self.client.beta.threads.create()
            st.session_state.thread_id = thread.id
        return st.session_state.thread_id

    def run(self):
        # Set page config and title
        st.set_page_config(page_title="BlacX x FINAS Assistant", layout="centered")
        
        # Custom CSS for Google-like styling
        st.markdown("""
            <style>
            .big-font {
                font-size:50px !important;
                font-weight:bold;
                text-align:center;
                margin-bottom:30px;
                background: linear-gradient(45deg, #1e3c72, #2a5298);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .search-box {
                border-radius:24px !important;
                border:1px solid #dfe1e5 !important;
                padding:10px 20px !important;
                width:100% !important;
                margin:20px 0 !important;
            }
            .stButton button {
                background-color:#f8f9fa;
                border:1px solid #f8f9fa;
                border-radius:4px;
                color:#3c4043;
                margin:11px 4px;
                padding:0 16px;
                height:36px;
                cursor:pointer;
            }
            .stButton button:hover {
                border:1px solid #dadce0;
                box-shadow:0 1px 1px rgba(0,0,0,.1);
            }
            
            /* Add RTL support for Arabic */
            [lang="ar"] {
                direction: rtl;
                text-align: right;
                font-family: 'Arial', sans-serif;
            }
            
            /* Adjust input fields for RTL when Arabic is selected */
            .rtl-support {
                direction: rtl;
                text-align: right;
            }

        
            
            .assistant-info {
                font-size: 0.9em;
                color: #666;
                margin-top: 5px;
            }
            </style>
            <div class="big-font">BlacX x FINAS</div>
        """, unsafe_allow_html=True)
        
        # Language selector and "New Conversation" button side by side
        languages = list(self.translations.keys())
        col_lang, col_button = st.columns([3, 1])
        
        with col_lang:
            selected_language = st.selectbox(
                "Language",
                languages,
                label_visibility="collapsed"
            )
        
        with col_button:
            if st.session_state.conversation_active:
                if st.button(self.get_text("start_new_conversation", selected_language)):
                    st.session_state.thread_id = None
                    st.session_state.conversation_active = False
                    st.rerun()

        # Add assistant selector with description
        st.markdown("<div class='assistant-selector'>", unsafe_allow_html=True)
        selected_assistant_name = st.selectbox(
            self.get_text("select_assistant", selected_language),
            list(self.assistants.keys()),
            format_func=lambda x: f"🤖 {x}",  # Add emoji to make it more visual
        )

        # Display assistant description
        assistant_descriptions = {
            "BARONIA_B": "https://f001.backblazeb2.com/file/KioskOrtanaProxy/CACA2CC9-E851-469B-851B-0FFE78D90A45.MP4",
            "FACE_OF_MALAYSIA": "https://f001.backblazeb2.com/file/KioskOrtanaProxy/CACA2CC9-E851-469B-851B-0FFE78D90A45.MP4",
            "MENJUNJUNG_KASIH": "https://f001.backblazeb2.com/file/KioskOrtanaProxy/A5118C34-0CC0-46FD-901D-FD3D2587BFC9.MP4"
        }
        st.markdown(f"<div class='assistant-info'>{assistant_descriptions.get(selected_assistant_name, '')}</div>", 
                    unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Use translated text throughout the interface
        rtl_class = "rtl-support" if selected_language == "عربي" else ""
        query = st.text_input(
            "",
            placeholder=self.get_text("placeholder", selected_language),
            label_visibility="collapsed",
            key="search_box",
            # Add HTML attributes for RTL support
            kwargs={
                "class": rtl_class,
                "dir": "rtl" if selected_language == "عربي" else "ltr"
            }
        )
        
        # Buttons with translations
        col1, col2 = st.columns([1, 1])
        with col1:
            search = st.button(
                self.get_text("ask_button", selected_language), 
                use_container_width=True
            )
        with col2:
            lucky = st.button(
                self.get_text("creative_button", selected_language), 
                use_container_width=True
            )
        
        # Suggested questions with translations
        st.markdown(f"### {self.get_text('suggested_questions', selected_language)}")
        suggestions = self.get_text("suggestions", selected_language)
        
        # Display suggestions in a grid
        cols = st.columns(2)
        for idx, suggestion in enumerate(suggestions):
            with cols[idx % 2]:
                if st.button(suggestion, key=f"sug_{idx}", use_container_width=True):
                    query = suggestion
                    search = True

        
        # Handle search with translated processing message
        if search or lucky:
            st.markdown("---")
            with st.spinner(self.get_text("processing", selected_language)):
                try:
                    # Get or create thread
                    thread_id = self.create_or_get_thread()
                    
                    # Determine the content to send
                    if lucky:  # I'm Feeling Creative button
                        if not query:  # If no query entered, use a random creative prompt
                            query = self.get_creative_prompt(selected_language)
                            st.info(f"Creative Prompt: {query}")
                        else:  # If query exists, enhance it creatively
                            creative_query = f"Please provide a creative and innovative response about: {query}. Think outside the box and suggest unique perspectives or possibilities while staying within FINAS guidelines."
                            query = creative_query

                    # Add message to thread
                    message = self.client.beta.threads.messages.create(
                        thread_id=thread_id,
                        role="user",
                        content=f"[Language: {selected_language}] {query}"
                    )
                    
                    # Create and run assistant
                    run = self.client.beta.threads.runs.create(
                        thread_id=thread_id,
                        assistant_id=self.ASSISTANT_ID
                    )
                    
                    # Wait for completion
                    while True:
                        run_status = self.client.beta.threads.runs.retrieve(
                            thread_id=thread_id,
                            run_id=run.id
                        )
                        if run_status.status == 'completed':
                            break
                        elif run_status.status in ['failed', 'cancelled', 'expired']:
                            st.error(f"Run failed with status: {run_status.status}")
                            return
                    
                    # Get all messages in the thread
                    messages = self.client.beta.threads.messages.list(
                        thread_id=thread_id
                    )
                    
                    # Display conversation history
                    st.markdown("### Conversation:")
                    for msg in messages.data:
                        role = "🧑" if msg.role == "user" else "🤖"
                        for content in msg.content:
                            if content.type == 'text':
                                st.markdown(f"""
                                <div style='background-color:{"#f0f2f6" if msg.role == "user" else "#f8f9fa"}; 
                                         padding:20px; 
                                         border-radius:10px;
                                         margin: 5px 0;'>
                                    <strong>{role}</strong>: {content.text.value}
                                </div>
                                """, unsafe_allow_html=True)
                    
                    # Mark conversation as active
                    st.session_state.conversation_active = True

                except Exception as e:
                    st.error(f"Error processing query: {str(e)}")

if __name__ == "__main__":
    app = AssistantUI()
    app.run()