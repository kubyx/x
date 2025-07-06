import os
import subprocess

def list_files(directory):
    """Belirtilen dizindeki dosyaları listele."""
    try:
        return os.listdir(directory)
    except Exception as e:
        return str(e)

def read_file(file_path):
    """Belirtilen dosyanın içeriğini oku."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except Exception as e:
        return str(e)

def execute_command(command):
    """Belirtilen komutu çalıştır."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return str(e)

# Örnek kullanım
if __name__ == "__main__":
    print("Dosyalar:", list_files("."))
    print("Dosya içeriği:", read_file("ornek.txt"))
    print("Komut sonucu:", execute_command("dir"))
