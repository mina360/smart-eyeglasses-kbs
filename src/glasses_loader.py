# glasses_loader.py
import pandas as pd
import traceback

class GlassesDataLoader:
    """
    تحميل وتنظيف بيانات النظارات من ملف Excel.
    """
    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        """
        تحميل وتنظيف بيانات النظارات من ملف Excel.
        """
        try:
            df = pd.read_excel(self.file_path)

            rename_mapping = {
                'Lane_Width': 'bridge', 'Frame_Width': 'frame_width', 'Weight': 'weight',
                'Style': 'professional_style', 'Frame ID': 'frame_id'
            }
            df.columns = df.columns.str.strip()
            existing_rename = {k: v for k, v in rename_mapping.items() if k in df.columns}
            df.rename(columns=existing_rename, inplace=True)
            df.columns = df.columns.str.lower()

            all_cols = [
                'frame_id', 'shape', 'material', 'size', 'gender', 'weight', 'bridge', 'bridge_width',
                'frame_width', 'rim', 'color', 'professional_style', 'athletic_category',
                'artistic_category', 'features', 'lens_width', 'lens_height', 'temple_length',
                'durability_rating', 'face_coverage', 'temple_grip', 'color_pattern', 'design_details'
            ]
            for col in all_cols:
                if col not in df.columns:
                    df[col] = pd.NA

            text_cols = [
                'frame_id', 'shape', 'material', 'size', 'gender', 'rim', 'color',
                'professional_style', 'athletic_category', 'artistic_category', 'face_coverage',
                'temple_grip', 'color_pattern', 'design_details'
            ]
            for col in text_cols:
                df[col] = df[col].fillna('n/a').astype(str).str.lower().str.strip()

            numeric_cols = [
                'weight', 'bridge', 'frame_width', 'lens_width', 'lens_height',
                'temple_length', 'durability_rating'
            ]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0).astype(float)
            
            if 'bridge_width' not in df.columns or df['bridge_width'].isnull().all():
                df['bridge_width'] = df['bridge']

            if 'features' in df.columns:
                df['features'] = df['features'].apply(
                    lambda x: [f.strip() for f in str(x).split(',') if f.strip()] if pd.notna(x) else []
                )
            else:
                df['features'] = [[] for _ in range(len(df))]

            print("✅ Glasses database loaded and cleaned successfully.")
            return df.to_dict(orient='records')

        except Exception as e:
            print(f"❌ CRITICAL ERROR in glasses_loader: {e}")
            traceback.print_exc()
            return []