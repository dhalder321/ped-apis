import boto3
import logging

class DBManager:

    @staticmethod
    def addRecordInDynamoTable(tableName, jsonData={}):

        try: 
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(tableName)
            response = table.put_item(
                Item= jsonData
            )
            return True
        
        except Exception as e:
            logging.error(e)
            return False
        
