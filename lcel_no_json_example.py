# lcel_no_json_example.py

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_ollama import ChatOllama
import re

# 1) Décomposeur : demander à LLM de renvoyer des sous-questions numérotées comme :
# "1. ...\n2. ...\n3. ..."
decompose_prompt = PromptTemplate.from_template(
    "Divisez la question en jusqu'à 3 sous-questions concises. "
    "Renvoyez-les sous forme de liste numérotée (1., 2., 3.), rien d'autre.\n\nQuestion:\n{question}"
)

decomposer = decompose_prompt | ChatOllama(model="llama3.2", temperature=0.0)


def parse_numbered_subquestions(base_msg):
    text = getattr(base_msg, "content", str(base_msg)).strip()
    # trouver les lignes commençant par "1." ou "1)"
    lines = re.split(r"\r?\n", text)
    subqs = []
    for line in lines:
        m = re.match(r"\s*\d+\s*[.)]\s*(.*\S.*)$", line)
        if m:
            subqs.append(m.group(1).strip())
    # solution de repli : si aucune correspondance n'est trouvée, traiter le texte entier comme une seule sous-question
    if not subqs and text:
        subqs = [text]
    return subqs


parse_subq_runnable = RunnableLambda(parse_numbered_subquestions)

# 2) Répondez à chaque sous-question en renvoyant du texte brut avec des lignes d'étiquette :
# "Réponse : <réponse en une ligne>\nÉtapes :\n- étape 1\n- étape 2"
answer_prompt = PromptTemplate.from_template(
    "Vous êtes un assistant concis. Pour la sous-question ci-dessous, veuillez fournir:\n"
    "Réponse: <réponse en une ligne>\nÉtapes:\n- <étape 1>\n- <étape 2>\nSoyez bref.\n\nSous-question: {subq}"
)

answer_chain = answer_prompt | ChatOllama(model="llama3.2", temperature=0.2)


def run_answers(subquestions):
    # Appel séquentiel (plus stable avec Ollama local)
    parsed = []
    for i, q in enumerate(subquestions, 1):
        print(f"  → Traitement sous-question {i}/{len(subquestions)}...")
        out = answer_chain.invoke({"subq": q})
        text = getattr(out, "content", str(out)).strip()
        # extraire les lignes de réponse et les puces des étapes
        answer_line = None
        steps = []
        for line in text.splitlines():
            if line.lower().startswith("réponse:"):
                answer_line = line.split(":", 1)[1].strip()
            elif re.match(r"\s*[-•]\s+", line):
                steps.append(re.sub(r"^\s*[-•]\s+", "", line).strip())
        # solution de repli : si rien n'est analysé, conserver le texte brut
        parsed.append({
            "answer": answer_line or text,
            "steps": steps or ["(aucune étape analysée)"],
            "raw": text
        })
    return parsed


run_answers_runnable = RunnableLambda(run_answers)

# 3) Combinaison : synthétiser la réponse courte finale à partir de la liste des sous-réponses simples
combine_prompt = PromptTemplate.from_template(
    "Synthétisez une seule réponse finale concise à partir de ces sous-réponses numérotées.\n\n"
    "Entrée (chaque élément est de type 'Réponse: ...' et 'Étapes: - ...'):\n{subanswers_text}\n\n"
    "Veuillez renvoyer exactement trois lignes:\n"
    "1) Réponse finale: <une ligne>\n"
    "2) Points clés: - <p1>; - <p2>\n"
    "3) Niveau de confiance: <faible/moyen/élevé>"
)


# Fonction auxiliaire pour formater les sous-réponses en un bloc de texte brut
def format_subanswers_block(ans_list):
    blocks = []
    for i, a in enumerate(ans_list, start=1):
        blocks.append(f"{i}. Réponse: {a['answer']}")
        blocks.append("   Étapes:")
        for s in a["steps"]:
            blocks.append(f"   - {s}")
    return "\n".join(blocks)


format_runnable = RunnableLambda(lambda answers: {"subanswers_text": format_subanswers_block(answers)})
combiner = format_runnable | combine_prompt | ChatOllama(model="llama3.2", temperature=0.0)

# Composition du pipeline
pipeline = decomposer | parse_subq_runnable | run_answers_runnable | combiner

if __name__ == "__main__":
    q = "Comment améliorer la sécurité d'une API REST qui gère des données sensibles?"
    
    print("=" * 60)
    print("PIPELINE LCEL - Démonstration")
    print("=" * 60)
    print(f"\n📝 Question: {q}\n")
    
    print("-" * 60)
    print("Étape 1: Décomposition en sous-questions...")
    decomposed = decomposer.invoke({"question": q})
    subqs = parse_numbered_subquestions(decomposed)
    print("\n📋 Sous-questions:")
    for i, sq in enumerate(subqs, 1):
        print(f"   {i}. {sq}")
    
    print("\n" + "-" * 60)
    print("Étape 2: Réponse à chaque sous-question...")
    answers = run_answers(subqs)
    print("\n📝 Sous-réponses:")
    for i, a in enumerate(answers, 1):
        print(f"\n   {i}. Réponse: {a['answer']}")
        print("      Étapes:")
        for s in a["steps"]:
            print(f"        - {s}")
    
    print("\n" + "-" * 60)
    print("Étape 3: Synthèse finale...")
    final = combiner.invoke(answers)
    
    print("\n" + "=" * 60)
    print("🎯 RÉSULTAT FINAL:")
    print("=" * 60)
    print(getattr(final, "content", str(final)))
