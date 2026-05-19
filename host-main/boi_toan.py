import random
import hashlib

def thuat_toan_boi_ten(ten):
    ten_chuan_hoa = ten.strip().lower()
    seed = int(hashlib.md5(ten_chuan_hoa.encode('utf-8')).hexdigest(), 16)
    random.seed(seed)
    phan_tram = random.randint(0, 100)
    
    kho_luu_tru = [
        f"Máy quét nhận diện bạn có {phan_tram}% độ 'Bóng'. Quá bất ngờ! 🏳️‍🌈",
        f"Chỉ số nhan sắc tiềm ẩn của bạn đang dừng ở mức {phan_tram}%.",
    ]
    return random.choice(kho_luu_tru)