# face_analyzer.py
import cv2
import mediapipe as mp
from math import sqrt
import sys
import collections
import collections.abc

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    collections.Mapping = collections.abc.Mapping
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Iterable = collections.abc.Iterable
    collections.Iterator = collections.abc.Iterator
    collections.KeysView = collections.abc.KeysView
    collections.ValuesView = collections.abc.ValuesView


class FaceAnalyzer:
    """
    تحليل صورة الوجه لتحديد الشكل والأبعاد.
    """
    def __init__(self):
        self.mp_face_mesh = mp.solutions.face_mesh
        
    def analyze_face(self, image_path):
        """
        يقوم بتحليل صورة الوجه باستخدام MediaPipe FaceMesh لتحديد شكل وأبعاد الوجه.
        """
        image_bgr = cv2.imread(image_path)
        if image_bgr is None: 
            raise ValueError(f"Image not found at path: {image_path}")
        
        h, w, _ = image_bgr.shape
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        
        with self.mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, refine_landmarks=True) as face_mesh:
            results = face_mesh.process(image_rgb)
            if not results.multi_face_landmarks: 
                raise ValueError("No face detected in the image")
            
            landmarks = results.multi_face_landmarks[0].landmark
            
            def to_px(l): return int(l.x * w), int(l.y * h)
            def euc(p1, p2): return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)
            
            try:
                
                scale_mm_per_px = 13 / (euc(to_px(landmarks[473]), to_px(landmarks[476])) * 2)
            except (ZeroDivisionError, IndexError):
                scale_mm_per_px = 0.25 
            face_width_px = euc(to_px(landmarks[135]), to_px(landmarks[352]))
            face_height_px = euc(to_px(landmarks[10]), to_px(landmarks[152]))
            forehead_width_px = euc(to_px(landmarks[54]), to_px(landmarks[284]))
            jaw_width_px = euc(to_px(landmarks[123]), to_px(landmarks[352]))
            
       
            face_width_cm = face_width_px * scale_mm_per_px / 10
            face_height_cm = face_height_px * scale_mm_per_px / 10
            forehead_width_cm = forehead_width_px * scale_mm_per_px / 10
            jaw_width_cm = jaw_width_px * scale_mm_per_px / 10
            
          
            face_shape = "Undefined"
            if abs(face_height_cm - face_width_cm) <= 1 and abs(face_height_cm - jaw_width_cm) <= 1 and abs(face_height_cm - forehead_width_cm) <= 1: 
                face_shape = 'Square'
            elif face_height_cm > forehead_width_cm and abs(forehead_width_cm - jaw_width_cm) <= 1 and abs(jaw_width_cm - face_width_cm) <= 1: 
                face_shape = 'Oblong'
            elif abs(face_height_cm - face_width_cm) <= 1 and abs(forehead_width_cm - jaw_width_cm) <= 1 and forehead_width_cm < face_height_cm: 
                face_shape = 'Round'
            elif face_height_cm > face_width_cm > forehead_width_cm > jaw_width_cm: 
                face_shape = 'Oval'
            elif forehead_width_cm < face_width_cm and face_width_cm < jaw_width_cm: 
                face_shape = 'Triangle'
            elif forehead_width_cm > face_width_cm and face_width_cm > jaw_width_cm: 
                face_shape = 'Heart'
            elif face_width_cm > forehead_width_cm and abs(forehead_width_cm - jaw_width_cm) <= 1: 
                face_shape = 'Diamond'
            else: 
                face_shape = 'Oval' 
                
            return {
                'face_shape': face_shape, 
                'face_width': face_width_cm, 
                'face_height': face_height_cm, 
                'forehead_width': forehead_width_cm, 
                'jaw_width': jaw_width_cm
            }