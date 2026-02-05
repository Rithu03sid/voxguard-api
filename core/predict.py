import random
def predict_voice(features):
    score = random.random()
    if score > 0.5:
        return "AI Generated", round(score * 100, 2)
    return "Human Voice", round((1 - score) * 100, 2)
