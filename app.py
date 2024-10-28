from flask import Flask, render_template, request
import os
import paramiko
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'YOUR_SECRET_KEY'

# Local and EC2 upload paths
UPLOAD_FOLDER = '/path/to/local/uploads'
EC2_UPLOAD_DIR = '/path/to/ec2/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# EC2 Connection details
EC2_HOST = 'YOUR_EC2_PUBLIC_IP'
EC2_USERNAME = 'YOUR_EC2_USERNAME'
EC2_KEY_PATH = '/path/to/your/key.pem'  # Ensure correct path

def upload_to_ec2(local_path, filename):
    """Uploads a file to the EC2 instance."""
    with paramiko.SSHClient() as ssh:
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(EC2_HOST, username=EC2_USERNAME, key_filename=EC2_KEY_PATH)
        with ssh.open_sftp() as sftp:
            sftp.put(local_path, os.path.join(EC2_UPLOAD_DIR, filename))

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/upload", methods=["POST", "GET"])
def upload():
    if request.method == "POST":
        file = request.files.get('file')
        if file and file.filename.lower().endswith(('.jpg', '.png', '.jpeg')):
            filename = secure_filename(file.filename)
            local_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(local_path)

            try:
                upload_to_ec2(local_path, filename)
                message = "File uploaded successfully to EC2!"
            except Exception as e:
                message = f"Error during upload: {e}"

            return render_template('upload.html', message=message)

    return render_template('upload.html')

@app.route('/uploads')
def show_uploads():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template('uploads.html', files=files)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
