import os
from openai import OpenAI
import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from langchain.text_splitter import RecursiveCharacterTextSplitter
from dotenv import load_dotenv
import re

def load_environment():
    """Load environment variables"""
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    
    return api_key

# Initialize Groq client
try:
    api_key = load_environment()
    groq_client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )
except Exception as e:
    st.error(f"Error initializing API client: {str(e)}")
    st.stop()

def extract_video_id(youtube_url):
    """Extract video ID from different YouTube URL formats"""
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',  # Standard and shared URLs
        r'(?:embed\/)([0-9A-Za-z_-]{11})',   # Embed URLs
        r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',  # Shortened URLs
        r'(?:shorts\/)([0-9A-Za-z_-]{11})',   # YouTube Shorts
        r'^([0-9A-Za-z_-]{11})$'  # Just the video ID
    ]
    
    youtube_url = youtube_url.strip()
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    raise ValueError("Could not extract video ID from URL")

def get_transcript(youtube_url):
    """Get transcript using YouTube Transcript API with cookies"""
    try:
        video_id = extract_video_id(youtube_url)
        
        # Get cookies file path
        cookies_file = os.getenv('COOKIE_PATH', os.path.join(os.path.dirname(__file__), 'cookies.txt'))
        
        
        if not os.path.exists(cookies_file):
            st.error("Cookie file not found. Please follow the setup instructions in the README.")
            st.error(f"Cookie file not found at: {cookies_file}")
            st.info("Please run init_cookies.bat to generate the cookie file")
            return None, None
            
        try:
            # Read cookies from file
            with open(cookies_file, 'r') as f:
                cookies_content = f.read()
                if not cookies_content.strip():
                    st.error("Cookie file is empty. Please re-export your YouTube cookies.")
                    return None, None
            
            # Get transcript with cookies
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id, cookies=cookies_file)
            
            try:
                transcript = transcript_list.find_manually_created_transcript()
            except:
                try:
                    transcript = next(iter(transcript_list))
                except Exception as e:
                    st.error("Your YouTube cookies might have expired. Please re-export your cookies and try again.")
                    return None, None
            
            full_transcript = " ".join([part['text'] for part in transcript.fetch()])
            language_code = transcript.language_code
            
            return full_transcript, language_code
                
        except Exception as e:
            st.error("Authentication failed. Please update your cookies.txt file with fresh YouTube cookies.")
            st.info("Tip: Sign in to YouTube again and re-export your cookies using the browser extension.")
            return None, None
            
    except Exception as e:
        st.error("Invalid YouTube URL. Please check the link and try again.")
        return None, None

def get_available_languages():
    """Return a dictionary of available languages with their prompts"""
    return {
        'en': {
            'name': 'English',
            'prompts': {
                'title': 'TITLE',
                'overview': 'OVERVIEW',
                'key_points': 'KEY POINTS',
                'takeaways': 'MAIN TAKEAWAYS',
                'context': 'CONTEXT & IMPLICATIONS'
            }
        },
        'de': {
            'name': 'Deutsch',
            'prompts': {
                'title': 'TITEL',
                'overview': 'ÜBERBLICK',
                'key_points': 'KERNPUNKTE',
                'takeaways': 'HAUPTERKENNTNISSE',
                'context': 'KONTEXT & AUSWIRKUNGEN'
            }
        },
        'es': {
            'name': 'Español',
            'prompts': {
                'title': 'TÍTULO',
                'overview': 'RESUMEN',
                'key_points': 'PUNTOS CLAVE',
                'takeaways': 'CONCLUSIONES PRINCIPALES',
                'context': 'CONTEXTO E IMPLICACIONES'
            }
        },
        'fr': {
            'name': 'Français',
            'prompts': {
                'title': 'TITRE',
                'overview': 'APERÇU',
                'key_points': 'POINTS CLÉS',
                'takeaways': 'POINTS ESSENTIELS',
                'context': 'CONTEXTE ET IMPLICATIONS'
            }
        },
        'it': {
            'name': 'Italiano',
            'prompts': {
                'title': 'TITOLO',
                'overview': 'PANORAMICA',
                'key_points': 'PUNTI CHIAVE',
                'takeaways': 'CONCLUSIONI PRINCIPALI',
                'context': 'CONTESTO E IMPLICAZIONI'
            }
        },
        'nl': {
            'name': 'Nederlands',
            'prompts': {
                'title': 'TITEL',
                'overview': 'OVERZICHT',
                'key_points': 'KERNPUNTEN',
                'takeaways': 'BELANGRIJKSTE INZICHTEN',
                'context': 'CONTEXT EN IMPLICATIES'
            }
        },
        'pl': {
            'name': 'Polski',
            'prompts': {
                'title': 'TYTUŁ',
                'overview': 'PRZEGLĄD',
                'key_points': 'KLUCZOWE PUNKTY',
                'takeaways': 'GŁÓWNE WNIOSKI',
                'context': 'KONTEKST I IMPLIKACJE'
            }
        },
        'ja': {
            'name': '日本語',
            'prompts': {
                'title': 'タイトル',
                'overview': '概要',
                'key_points': '重要ポイント',
                'takeaways': '主な結論',
                'context': '文脈と影響'
            }
        },
        'zh': {
            'name': '中文',
            'prompts': {
                'title': '标题',
                'overview': '概述',
                'key_points': '要点',
                'takeaways': '主要结论',
                'context': '背景与影响'
            }
        },
        'ru': {
            'name': 'Русский',
            'prompts': {
                'title': 'ЗАГОЛОВОК',
                'overview': 'ОБЗОР',
                'key_points': 'КЛЮЧЕВЫЕ МОМЕНТЫ',
                'takeaways': 'ОСНОВНЫЕ ВЫВОДЫ',
                'context': 'КОНТЕКСТ И ЗНАЧЕНИЕ'
            }
        }
    }

def get_language_instructions(lang_code):
    """Return language-specific instructions for the AI"""
    instructions = {
        'de': "Fasse den Inhalt auf Deutsch zusammen. Verwende natürliche, flüssige deutsche Sprache.",
        'es': "Resume el contenido en español. Utiliza un español natural y fluido.",
        'fr': "Résume le contenu en français. Utilise un français naturel et fluide.",
        'it': "Riassumi il contenuto in italiano. Usa un italiano naturale e fluido.",
        'nl': "Vat de inhoud samen in het Nederlands. Gebruik natuurlijk, vloeiend Nederlands.",
        'pl': "Podsumuj treść po polsku. Użyj naturalnego, płynnego języka polskiego.",
        'ja': "内容を日本語で要約してください。自然で流暢な日本語を使用してください。",
        'zh': "用中文总结内容。使用自然流畅的中文。",
        'ru': "Подведите итог на русском языке. Используйте естественный, плавный русский язык.",
        'en': "Summarize the content in English. Use natural, fluent English."
    }
    return instructions.get(lang_code, instructions['en'])

def create_summary_prompt(text, target_language_code, mode='video'):
    """Create an optimized prompt for summarization in the target language and mode"""
    languages = get_available_languages()
    language_data = languages[target_language_code]
    prompts = language_data['prompts']
    lang_instructions = get_language_instructions(target_language_code)
    
    if mode == 'podcast':
        system_prompt = f"""You are an expert content analyst and summarizer. {lang_instructions}
        Create a comprehensive podcast-style summary that feels natural and engaging in the target language."""

        user_prompt = f"""Please provide a detailed podcast-style summary in {language_data['name']}. 
        Structure your response as follows:

        🎙️ {prompts['title']}: Create an engaging title

        🎧 {prompts['overview']} (3-5 sentences):
        - Provide a detailed context and main purpose

        🔍 {prompts['key_points']}:
        - Deep dive into the main arguments
        - Include specific examples and anecdotes
        - Highlight unique perspectives and expert opinions

        📈 {prompts['takeaways']}:
        - List 5-7 practical insights
        - Explain their significance and potential impact

        🌐 {prompts['context']}:
        - Broader context discussion
        - Future implications and expert predictions

        Text to summarize: {text}"""

    else:
        system_prompt = f"""You are an expert content analyst and summarizer. {lang_instructions}
        Create a comprehensive video summary that feels natural and engaging in the target language."""

        user_prompt = f"""Please provide a detailed video summary in {language_data['name']}. 
        Structure your response as follows:

        🎯 {prompts['title']}: Create a descriptive title

        📝 {prompts['overview']} (2-3 sentences):
        - Provide a brief context and main purpose

        🔑 {prompts['key_points']}:
        - Extract and explain the main arguments
        - Include specific examples
        - Highlight unique perspectives

        💡 {prompts['takeaways']}:
        - List 3-5 practical insights
        - Explain their significance

        🔄 {prompts['context']}:
        - Broader context discussion
        - Future implications

        Text to summarize: {text}"""

    return system_prompt, user_prompt

def summarize_with_langchain_and_openai(transcript, language_code, model_name='llama-3.1-8b-instant', mode='video'):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=7000,
        chunk_overlap=1000,
        length_function=len
    )
    texts = text_splitter.split_text(transcript)
    
    intermediate_summaries = []
    lang_instructions = get_language_instructions(language_code)
    
    for i, text_chunk in enumerate(texts):
        system_prompt = f"""You are an expert content summarizer. {lang_instructions}
        Create a detailed summary of section {i+1} that maintains important details, 
        arguments, and connections."""

        user_prompt = f"""Create a detailed summary of the following section.
        Maintain all important information, arguments, and connections.
        Pay special attention to:
        - Main topics and arguments
        - Important details and examples
        - Connections with other mentioned topics
        - Key statements and conclusions

        Text: {text_chunk}"""
        
        try:
            response = groq_client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=8000
            )
            
            summary = response.choices[0].message.content
            intermediate_summaries.append(summary)
            
        except Exception as e:
            st.error(f"Error with Groq API during intermediate summarization: {str(e)}")
            return None
    
    combined_summary = "\n\n=== Next Section ===\n\n".join(intermediate_summaries)
    
    final_system_prompt, final_user_prompt = create_summary_prompt(combined_summary, language_code, mode)
    
    try:
        final_response = groq_client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": final_system_prompt},
                {"role": "user", "content": final_user_prompt}
            ],
            temperature=0.7,
            max_tokens=8000
        )
        
        final_summary = final_response.choices[0].message.content
        return final_summary
    except Exception as e:
        st.error(f"Error with Groq API during final summarization: {str(e)}")
        return None

def main():
    st.title('📺 Advanced YouTube Video Summarizer')
    st.markdown("""
    This tool creates comprehensive summaries of YouTube videos using advanced AI technology.
    It works with both videos that have transcripts and those that don't!
    """)
    
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        link = st.text_input('🔗 Enter YouTube video URL:')
    
    with col2:
        languages = get_available_languages()
        language_options = {lang_data['name']: code for code, lang_data in languages.items()}
        target_language = st.selectbox(
            '🌍 Select Summary Language:',
            options=list(language_options.keys()),
            index=0
        )
        target_language_code = language_options[target_language]

    with col3:
        mode = st.selectbox(
            '🎙️ Select Mode:',
            options=['Video', 'Podcast'],
            index=0
        )
        mode = mode.lower()

    if st.button('Generate Summary'):
        if link:
            try:
                with st.spinner('Processing...'):
                    progress = st.progress(0)
                    status_text = st.empty()

                    status_text.text('📥 Fetching video transcript...')
                    progress.progress(25)

                    transcript, _ = get_transcript(link)

                    status_text.text(f'🤖 Generating {target_language} summary...')
                    progress.progress(75)

                    summary = summarize_with_langchain_and_openai(
                        transcript, 
                        target_language_code,
                        model_name='llama-3.1-8b-instant',
                        mode=mode
                    )

                    status_text.text('✨ Summary Ready!')
                    st.markdown(summary)
                    progress.progress(100)
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning('Please enter a valid YouTube link.')

if __name__ == "__main__":
    main()