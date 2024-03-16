import boto3
import logging
# from boto3 import TypeSerializer, TypeDeserializer
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer

class DBManager:

    @staticmethod
    def updateRecordInDynamoTable(tableName, partitionKeyCol, \
                                  partitionKeyValue, sortKeyCol, sortKeyValue,  jsonData):

        try: 
            client = boto3.client('dynamodb')
            resp = client.query(
                                TableName=tableName,
                                KeyConditionExpression='#pk = :pk',
                                ExpressionAttributeValues={':pk': {'N': partitionKeyValue}},
                                ExpressionAttributeNames={'#pk': partitionKeyCol},
                                # ScanIndexForward=False,
                                # ProjectionExpression=partitionKeyColumn,
                                Limit=1
            )
            # print(resp['Items'])
            if 'Items' in resp and len(resp['Items']) > 0: 
                jsonBody = DBManager.dynamo_to_python(resp['Items'][0])
            else:
                raise Exception("In updateRecordInDynamoTable method: No record found to be updated")

            #remove the partition key and sort key and readd them
            # if partitionKeyCol in jsonBody:
            #     jsonBody.pop(partitionKeyCol)
            # if sortKeyCol in jsonBody:
            #     jsonBody.pop(sortKeyCol)
            # jsonBody[partitionKeyCol] = int(partitionKeyValue)
            # jsonBody[sortKeyCol] = int(sortKeyValue)

            #merge rest of the json data
            jsonBody.update(jsonData)
            # print(jsonBody)

            # do the final put
            dynamodb = boto3.resource('dynamodb')
            table = dynamodb.Table(tableName)
            response = table.put_item(Item=jsonBody)

            return partitionKeyValue

        except Exception as e:
            logging.error("Error occured in updateRecordInDynamoTable method: " + str(e))
            return False
        
    @staticmethod
    # Function to get the highest fileid value
    def get_highest_fileid(table_name, index_key_column, partitionKeyColumn, \
                           index_name, index_key_value="99"):

        client = boto3.client('dynamodb')

        # Define the request parameters
        response = client.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression='#pk = :pk',
            ExpressionAttributeValues={':pk': {'N': index_key_value}},
            ExpressionAttributeNames={'#pk': index_key_column},
            ScanIndexForward=False,
            ProjectionExpression=partitionKeyColumn,
            Limit=1
        )

        # return the highest value
        if 'Items' in response and len(response['Items']) > 0: 
            return int(response['Items'][0][partitionKeyColumn]['N'])
        return 0

    

    @staticmethod
    # Insert item with auto-incremented partition key
    def addRecordInDynamoTableWithAutoIncrKey(tableName, indexKeyCol, partitionKey, gsiName, jsonBody):
        
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table(tableName)

        try:
            next_fileid = DBManager.get_highest_fileid(tableName, indexKeyCol, partitionKey, gsiName) + 1
            jsonBody[partitionKey] = next_fileid

            response = table.put_item(Item=jsonBody)
            return next_fileid
        
        except Exception as e:
            logging.error("Error occured in addRecordInDynamoTableWithAutoIncrKey method: " + str(e))
            return None
        

    def dynamo_to_python(dynamo_object: dict) -> dict:
        deserializer = TypeDeserializer()
        return {
            k: deserializer.deserialize(v) 
            for k, v in dynamo_object.items()
        }  
  
    def python_to_dynamo(python_object: dict) -> dict:
        serializer = TypeSerializer()
        return {
            k: serializer.serialize(v)
            for k, v in python_object.items()
        }
    