import os, json
try:
    import google.generativeai as genai
except ImportError:
    genai = None

class LLMClient:
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "OPENAI").upper()
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None
        if self.provider == "OPENAI":
            from openai import OpenAI
            self._client = OpenAI()
        elif self.provider == "GOOGLE":
            if genai is None:
                raise ImportError("google-generativeai não instalado. Execute: pip install google-generativeai")
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise ValueError("Defina a variável de ambiente GOOGLE_API_KEY com sua chave da API Gemini.")
            genai.configure(api_key=api_key)
            self._client = genai

    def complete_json(self, prompt: str, system: str = "", temperature: float = 0.0, max_tokens: int = 800) -> str:
        # Retorna JSON (texto) usando Chat Completions com response_format=json_object.
        if self.provider == "OPENAI":
            resp = self._client.chat.completions.create(
                model=self.model,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={ "type": "json_object" },
                messages=[
                    {"role":"system","content": system or "Responda apenas com JSON válido, sem comentários."},
                    {"role":"user","content": prompt}
                ],
            )
            return resp.choices[0].message.content
        elif self.provider == "GOOGLE":
            model_name = os.getenv("GOOGLE_MODEL", "gemini-pro")
            system_message = system or "Responda apenas com JSON válido, sem comentários."
            full_prompt = f"{system_message}\nUsuário: {prompt}"
            model = self._client.GenerativeModel(model_name)
            response = model.generate_content(full_prompt, generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens
            })
            import re
            match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if match:
                return match.group(0)
            return response.text
        # MOCK (fallback)
        if '"paginas"' in prompt and '"criterio"' in prompt:
            return json.dumps({"criterio": "eficiencia_energetica", "paginas": [12, 13]})
        mock = {
            "criterio": "eficiencia_energetica",
            "presenca": "parcial",
            "risco_greenwashing": "medio",
            "evidencias": [{"doc": "edital.pdf", "pagina": 12, "trecho": "Exige classe A (ENCE), sem detalhar norma."}],
            "observacoes": "Falta norma/ensaio; há referência vaga."
        }
        return json.dumps(mock, ensure_ascii=False)
