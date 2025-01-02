from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
import google.generativeai as genai
from fastapi.staticfiles import StaticFiles
import requests,random

GEMINI_API_KEY = "AIzaSyDWuh6JDfGppgGyKCHRKpKMfFmP0EPYpe8"
genai.configure(api_key=GEMINI_API_KEY)
TENOR_API_KEY = "AIzaSyDuN550ygThE8-A0nFuJGXcgM3eNVCwNW8"
CKEY = "Anime"
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


class CommandPayload(BaseModel):
    command: str


class CSSPayload(BaseModel):
    css: str


def generate_css_with_gemini(command: str) -> str:
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = (
        f"You are a CSS generator AI. Convert the following command into valid CSS: {command}"
    )
    try:
        response = model.generate_content([prompt])
        print("Gemini API Response:", response.text)

        # Clean the response to remove Markdown-style formatting (e.g., ```css and ```)
        cleaned_css = response.text.replace("```css", "").replace("```", "").strip()

        print("Cleaned CSS:", cleaned_css)
        return cleaned_css

    except Exception as e:
        print(f"Error in Gemini API call: {e}")
        raise HTTPException(status_code=500, detail=f"Error in Gemini API: {str(e)}")


# Endpoint to handle CSS application
@app.post("/apply-css/")
async def apply_css(payload: CSSPayload):
    command = payload.css.strip()

    if not command:
        raise HTTPException(status_code=400, detail="CSS command is empty.")

    try:
        generated_css = generate_css_with_gemini(command)
        print("Command:", command)
        print("Generated CSS:", generated_css)
        
        # Save the CSS to a file
        css_file_path = "static/dynamic_styles.css"
        with open(css_file_path, "w") as file:
            file.write(generated_css)

        return {"message": "CSS applied successfully.", "file": css_file_path}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while applying CSS: {str(e)}"
        )


def generate_js_with_gemini(command: str) -> str:
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    prompt = (
        f"You are a JavaScript generator AI. Convert the following command into valid, plain JavaScript code: {command}. "
        f"Ensure the response contains only executable JavaScript without any enclosing tags or unnecessary prefixes like 'javascript:'."
        f"Also, avoid using 'console.log()' or similar functions in the response."
        f"Please provide the JavaScript code only."
        f"Try to display the implementation of the command in a div in the section with id=dynamic in the frontend."
        f"whatever you display apply some styles to it."
    )
    
    try:
        response = model.generate_content([prompt])
        print("Gemini API Response:", response.text)

        cleaned_js = (
            response.text
            .replace("```js", "")  
            .replace("```", "")
            .replace("javascript", "")  
            .strip()  
        )

        print("Cleaned JavaScript:", cleaned_js)
        return cleaned_js

    except Exception as e:
        print(f"Error in Gemini API call: {e}")
        raise HTTPException(status_code=500, detail=f"Error in Gemini API: {str(e)}")


@app.post("/apply-changes/")
async def apply_changes(payload: CommandPayload, request: Request):
    command = payload.command.strip()

    if not command:
        raise HTTPException(status_code=400, detail="Command is empty.")

    # Determine the type of request (CSS or JS)
    change_type = request.headers.get("X-Change-Type", "").lower()

    if change_type not in ["css", "js"]:
        raise HTTPException(status_code=400, detail="Invalid change type. Use 'css' or 'js'.")

    try:
        if change_type == "css":
            # Generate and save CSS
            generated_css = generate_css_with_gemini(command)
            css_file_path = "static/dynamic_styles.css"
            with open(css_file_path, "w") as file:
                file.write(generated_css)

            return {"message": "CSS applied successfully.", "file": css_file_path, "css": generated_css}

        elif change_type == "js":
            # Generate and save JavaScript
            generated_js = generate_js_with_gemini(command)
            js_file_path = "static/dynamic_script.js"
            with open(js_file_path, "w") as file:
                file.write(generated_js)

            return {"message": "JavaScript applied successfully.", "file": js_file_path, "js": generated_js}

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while applying {change_type.upper()}: {str(e)}"
        )


# Home route to serve index.html
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    with open("static/dynamic_script.js", "w") as file:
        file.write("// Dynamic JavaScript")
   
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/anime-of-the-day")
async def get_anime_of_the_day():
    """
    Fetches a random anime GIF based on the search term using the Tenor API.
    """
    try:
        anime_list = ["naruto", "jujutsu kaisen", "demon slayer", "one piece", "deathnote","spy x family","tokyo revengers"]
        random_anime = random.choice(anime_list)
        random_offset = random.randint(0, 50)
        url = (
            f"https://tenor.googleapis.com/v2/search?q={random_anime}"
            f"&key={TENOR_API_KEY}&client_key={CKEY}&limit=1&random=true&pos={random_offset}"
        )
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if "results" in data and len(data["results"]) > 0:
                gif_url = data["results"][0]["media_formats"]["gif"]["url"]
                return {"gif_url": gif_url}
            else:
                raise HTTPException(status_code=404, detail="No GIFs found for the given search term.")
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch data from Tenor API.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))