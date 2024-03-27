import pickle


with open("facial_encodings.pkl", "rb") as f:
    known_face_encodings = pickle.load(f)


print(type(known_face_encodings))

print(known_face_encodings)