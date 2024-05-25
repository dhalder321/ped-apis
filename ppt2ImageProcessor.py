import sys
import json
from ppt2image import getImagesFromS3PPT
from common.globals import Utility

def main():
    if len(sys.argv) != 2:
        print("Usage: ppt2ImageProcessor.py '<json_message>'")
        sys.exit(1)

    json_message = sys.argv[1]

    try:
        data = json.loads(json_message)
        print("Received JSON data:", data)
        # Process the data here
        if 'Body' in data:

            msg = json.loads(data['Body'])
            if 's3DirPath' in msg and msg['s3DirPath'] is not None and msg['s3DirPath'] != '' and\
                'fileName' in msg and msg['fileName'] is not None and msg['fileName'] != '':
                imgPath = getImagesFromS3PPT(Utility.S3BUCKE_NAME, msg['s3DirPath'], 
                                            Utility.WINDOWS_LOCAL_PATH, msg['fileName'])
                if imgPath is None:
                    print(f"Image conversion from PPT failed.")
                    sys.exit(1)
                    
                return imgPath
            
            else:
                print(f"Invalid JSON message.")
                sys.exit(1)
        else:
            print(f"Invalid JSON message.")
            sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"Invalid JSON message: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error in ppt2ImageProcessor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
