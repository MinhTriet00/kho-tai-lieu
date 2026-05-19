from flask import Flask, render_template, request
from boi_toan import thuat_toan_boi_ten # <--- Thêm dòng này

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        ten_nguoi_dung = request.form.get('ten')
        ket_qua_boi = thuat_toan_boi_ten(ten_nguoi_dung) # Gọi hàm như bình thường
        return render_template('index.html', ten=ten_nguoi_dung, ket_qua=ket_qua_boi)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)