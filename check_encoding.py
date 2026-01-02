import chardet

def check_file(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read()
        result = chardet.detect(rawdata)
        encoding = result['encoding']
        print(f"File: {file_path}")
        print(f"Detected encoding: {encoding}")
        
        try:
            content = rawdata.decode(encoding)
            lines = content.splitlines()
            for i, line in enumerate(lines):
                if 'python-dotenv' in line:
                    print(f"Line {i+1}: {line}")
        except Exception as e:
            print(f"Error decoding: {e}")

check_file(r'c:\Users\nagam\OneDrive\Desktop\campus_mart\requirements.txt')
check_file(r'c:\Users\nagam\OneDrive\Desktop\campus_mart\campusmart\requirements.txt')
