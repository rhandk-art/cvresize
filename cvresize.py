# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 18:48:55 2025

@author: hpuser
"""
import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io 

def load_image(image_file):
    """Membaca file yang diunggah dan mengonversinya menjadi objek PIL dan array numpy (OpenCV)."""
    # Untuk PIL (mendapatkan metadata)
    img_pil = Image.open(image_file)
    
    # Untuk OpenCV (pemrosesan gambar)
    img_cv = np.array(img_pil.convert('RGB'))
    
    # Konversi RGB ke BGR karena OpenCV secara default menggunakan BGR
    img_cv_bgr = cv2.cvtColor(img_cv, cv2.COLOR_RGB2BGR)
    
    return img_pil, img_cv_bgr

def display_image_info(img_cv, img_pil):
    """Menampilkan informasi terkait gambar."""
    st.subheader("🖼️ Informasi Gambar Asli")
    
    # Informasi dari array numpy/OpenCV
    height, width, channels = img_cv.shape
    st.write(f"**Format:** JPG/PNG (Sesuai unggahan)")
    st.write(f"**Dimensi Pixel (Lebar x Tinggi):** {width} x {height} px")
    st.write(f"**Jumlah Channel:** {channels} (Biasanya 3: Merah, Hijau, Biru)")
    
    # Informasi tambahan (metadata) dari PIL
    try:
        if img_pil.info:
            st.write("**Metadata (Exif):**")
            st.json(img_pil.info)
    except:
        st.write("Metadata tidak tersedia atau tidak dapat dibaca.")

def rotate_image(image_cv, angle):
    """Melakukan rotasi pada gambar (array NumPy)."""
    if angle == "90° Kanan":
        return cv2.rotate(image_cv, cv2.ROTATE_90_CLOCKWISE)
    elif angle == "90° Kiri":
        return cv2.rotate(image_cv, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif angle == "180°":
        return cv2.rotate(image_cv, cv2.ROTATE_180)
    return image_cv

# --- FUNGSI MODIFIKASI: Menerima parameter format dan kualitas ---
def to_downloadable_bytes(image_cv_bgr, format="PNG", quality=95):
    """Mengonversi gambar OpenCV (BGR) menjadi bytes yang dapat diunduh."""
    # Konversi BGR ke RGB
    image_rgb = cv2.cvtColor(image_cv_bgr, cv2.COLOR_BGR2RGB)
    # Konversi array numpy ke objek PIL
    img_pil = Image.fromarray(image_rgb)
    
    # Simpan objek PIL ke buffer bytes
    buf = io.BytesIO()
    
    # Simpan ke buffer dengan format dan kualitas yang ditentukan
    if format == "JPEG":
        img_pil.save(buf, format=format, quality=quality, optimize=True)
    else: # Default ke PNG (lossless)
        img_pil.save(buf, format="PNG")
        
    return buf.getvalue()

def clear_session_state():
    """Fungsi pembantu untuk menghapus data pemrosesan dari session state."""
    st.session_state.resized_image_bgr = None
    st.session_state.display_image_rgb = None
    # Hapus juga key-key lain yang mungkin disimpan jika ada
    keys_to_delete = ['rotation_select', 'resize_width', 'resize_height', 'download_format', 'jpeg_quality'] 
    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]


def main():
    """Fungsi utama aplikasi Streamlit."""
    st.title("💻 Computer Vision Image Processor (Streamlit)")
    st.markdown("Unggah file gambar untuk melihat informasi dan memodifikasi ukurannya.")

    # Inisialisasi session state untuk menyimpan gambar hasil resize
    if 'resized_image_bgr' not in st.session_state:
        st.session_state.resized_image_bgr = None
    if 'display_image_rgb' not in st.session_state:
        st.session_state.display_image_rgb = None
    # Tambahkan status untuk notifikasi resize
    if 'resize_status' not in st.session_state:
        st.session_state.resize_status = False

    # Menu Unggah File
    uploaded_file = st.file_uploader(
        "Pilih Gambar...", 
        type=["jpg", "jpeg", "png"]
    )
    
    # SCRIPT MODIFIKASI UNTUK MENGHAPUS RIWAYAT
    if uploaded_file is None and st.session_state.resized_image_bgr is not None:
        clear_session_state()
        st.rerun() 
    # ======================================================

    if uploaded_file is not None:
        # Memuat gambar untuk pemrosesan
        img_pil, img_cv_bgr = load_image(uploaded_file)
        
        # --- Bagian 1: Tampilkan Informasi Gambar Asli ---
        st.subheader("✨ Gambar Asli")
        st.image(uploaded_file, caption=f"File: {uploaded_file.name}", use_container_width=True)
        display_image_info(img_cv_bgr, img_pil)
        
        st.markdown("---")

        # --- Bagian 2: Modifikasi Ukuran Pixel (Resize) ---
        st.subheader("📏 Modifikasi Ukuran Pixel (Resize)")

        # Ambil dimensi asli
        h_original, w_original, _ = img_cv_bgr.shape

        # Mengambil nilai lama dari session state (jika ada) atau menggunakan default
        default_width = st.session_state.get('resize_width', int(w_original / 2))
        default_height = st.session_state.get('resize_height', int(h_original * (default_width / w_original)))

        # Input pengguna untuk ukuran baru
        col1, col2 = st.columns(2)
        with col1:
            new_width = st.number_input(
                "Lebar Baru (px)", 
                min_value=1, 
                value=default_width, 
                step=10,
                key="resize_width" 
            )
        with col2:
            new_height = st.number_input(
                "Tinggi Baru (px)", 
                min_value=1, 
                value=default_height, 
                step=10,
                key="resize_height" 
            )

        if st.button("Resize Gambar", key="do_resize_button"): 
            st.session_state.resize_status = False # Reset status
            if new_width > 0 and new_height > 0:
                try:
                    # Lakukan operasi resize menggunakan OpenCV
                    resized_img_bgr_temp = cv2.resize(
                        img_cv_bgr, 
                        (new_width, new_height), 
                        interpolation=cv2.INTER_LINEAR 
                    )
                    
                    # Simpan gambar hasil resize ke session state
                    st.session_state.resized_image_bgr = resized_img_bgr_temp
                    st.session_state.display_image_rgb = cv2.cvtColor(resized_img_bgr_temp, cv2.COLOR_BGR2RGB)
                    st.session_state.resize_status = True # Set status berhasil
                    st.success(f"Gambar berhasil di-resize menjadi {new_width} x {new_height} px.")
                    
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat melakukan resize: {e}")
            else:
                st.warning("Lebar dan Tinggi harus lebih besar dari 0.")
            # Rerun setelah resize untuk menampilkan gambar di bagian bawah (Modifikasi)
            st.rerun() 
        
        # --- Bagian Rotasi dan Unduh (Hanya muncul setelah gambar di-resize) ---
        if st.session_state.resized_image_bgr is not None:
            st.markdown("---")
            st.subheader("🔄 Rotasi, Format, & Unduh Gambar")

            # Kolom untuk Rotasi
            col_rot, col_btn = st.columns([0.7, 0.3])
            current_rotation = st.session_state.get('rotation_select', "Tidak Ada")
            rotation_options = ["Tidak Ada", "90° Kanan", "90° Kiri", "180°"]
            if current_rotation not in rotation_options:
                current_rotation = "Tidak Ada"

            with col_rot:
                rotation_angle = st.selectbox(
                    "Pilih Rotasi:",
                    rotation_options,
                    index=rotation_options.index(current_rotation),
                    key="rotation_select" 
                )
            
            with col_btn:
                st.write("") 
                st.write("")
                if st.button("Terapkan Rotasi & Perbarui Tampilan", key="apply_rotation_button"):
                    current_image_to_rotate = st.session_state.resized_image_bgr
                    final_processed_image_bgr = rotate_image(current_image_to_rotate, rotation_angle)
                    
                    st.session_state.resized_image_bgr = final_processed_image_bgr 
                    st.session_state.display_image_rgb = cv2.cvtColor(final_processed_image_bgr, cv2.COLOR_BGR2RGB)
                    
                    # Tampilkan notifikasi dengan dimensi baru
                    h_rotated, w_rotated, _ = final_processed_image_bgr.shape
                    st.success(f"Gambar telah dirotasi {rotation_angle}. Dimensi baru: {w_rotated} x {h_rotated} px.")
                    # Rerun setelah rotasi untuk menampilkan gambar di bagian Modifikasi
                    st.rerun()
            
            if st.session_state.display_image_rgb is not None:
                # Ambil dimensi gambar hasil modifikasi terakhir
                h_final, w_final, _ = st.session_state.display_image_rgb.shape
                
                # Tampilkan informasi hasil modifikasi
                st.subheader(f"🎨 Gambar Hasil Modifikasi ({w_final} x {h_final} px)")
                
                # Tampilkan gambar. Gunakan use_column_width=True untuk menghindari overflow
                # tetapi subheader sudah mencantumkan resolusi yang akurat.
                st.image(
                    st.session_state.display_image_rgb, 
                    use_container_width=True, 
                    caption="Gambar Hasil Modifikasi"
                )
                
                st.markdown("---")
                st.markdown("**Pengaturan Unduh:**")
                
                # Input Pengaturan Format & Kualitas Unduh
                col_format, col_quality = st.columns(2)
                
                with col_format:
                    download_format = st.selectbox(
                        "Pilih Format Unduhan:",
                        ["PNG (Lossless/Ukuran Besar)", "JPEG (Kompresi/Ukuran Kecil)"],
                        key="download_format"
                    )
                    
                output_format = "PNG"
                file_ext = "png"
                image_quality = 95
                
                with col_quality:
                    if "JPEG" in download_format:
                        output_format = "JPEG"
                        file_ext = "jpeg"
                        image_quality = st.slider(
                            "Kualitas JPEG (1=Terburuk, 100=Terbaik)",
                            min_value=10, 
                            max_value=100, 
                            value=95, 
                            step=5,
                            key="jpeg_quality"
                        )
                    else:
                        st.markdown("*(PNG tidak menggunakan pengaturan kualitas)*")

                # Persiapan Bytes Unduhan
                image_bytes = to_downloadable_bytes(st.session_state.resized_image_bgr, 
                                                     format=output_format, 
                                                     quality=image_quality)
                
                # Tombol Unduh
                st.download_button(
                    label=f"⬇️ Unduh Gambar Hasil Modifikasi ({output_format})",
                    data=image_bytes,
                    file_name=f"gambar_modifikasi_{w_final}x{h_final}.{file_ext}",
                    mime=f"image/{file_ext}",
                    key="download_button"
                )

if __name__ == '__main__':
    main()