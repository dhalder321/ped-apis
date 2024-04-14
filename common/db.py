import boto3
import logging
# from boto3 import TypeSerializer, TypeDeserializer
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from boto3.dynamodb.conditions import Key


class DBManager:

    dbSession = boto3.Session()
    dynamodb = dbSession.resource('dynamodb')

    dbClient = boto3.client('dynamodb')

    @staticmethod
    def updateRecordInDynamoTable(tableName, partitionKeyCol, \
                                  partitionKeyValue, sortKeyCol, sortKeyValue,  jsonData):

        try: 
             
            resp = DBManager.dbClient.query(
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

            #merge rest of the json data
            jsonBody.update(jsonData)
            # print(jsonBody)

            # do the final put
            table = DBManager.dynamodb.Table(tableName)
            response = table.put_item(Item=jsonBody)

            return partitionKeyValue

        except Exception as e:
            logging.error("Error occured in updateRecordInDynamoTable method: " + str(e))
            return None
        
    @staticmethod
    # Function to get the highest fileid value
    def get_highest_fileid(table_name, index_key_column, partitionKeyColumn, \
                           index_name, index_key_value="99"):

        

        # Define the request parameters
        response = DBManager.dbClient.query(
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
        
        
        table = DBManager.dynamodb.Table(tableName)

        try:
            next_fileid = DBManager.get_highest_fileid(tableName, indexKeyCol, partitionKey, gsiName) + 1
            print(next_fileid)
            jsonBody[partitionKey] = next_fileid

            response = table.put_item(Item=jsonBody)
            return next_fileid
        
        except Exception as e:
            logging.error("Error occured in addRecordInDynamoTableWithAutoIncrKey method: " + str(e))
            return None
        

    @staticmethod
    def getDBItemByIndex(tableName, indexCol, indexName, indexColValue):
        
        try:
            
            table = DBManager.dynamodb.Table(tableName)

            response = table.query(
                            IndexName= indexName, 
                            KeyConditionExpression=Key(indexCol).eq(indexColValue) 
                        )
            # print(response)
            return response['Items'] if 'Items' in response else None
        
        except Exception as e:
            logging.error("Error occured in getDBItemByIndex method: " + str(e))
            return None
    
    ##########################################################################
    #
    # Example usage:
    # response = getDBItems(
    #     table_name='YourTableName',
    #     partition_key_name='PartitionKeyName',
    #     partition_key_value='PartitionKeyValue',
    #     sort_key_name='SortKeyName',
    #     sort_key_value='SortKeyValue',
    #     filter_expression='OtherColumnName = :value',
    #     value='example_value',
    #     projection_expression='Attribute1, Attribute2'
    # )
    # DBManager.getDBItems(table_name=DBTables.User_Table_Name, \
                                            # sort_key_name="email", sort_key_value=email, \
                                            # filter_expression= "pwdEn = :value", \
                                            # value = pwdEn, \
                                            # projection_expression="userid, firstName, lastName", \
                                            # index_name="email-index")
    #####################################################################################
    @staticmethod
    def getDBItems(table_name, filter_expression=None, \
                       projection_expression=None, index_name=None, \
                        partition_key_name=None, partition_key_value=None, \
                            sort_key_name=None, sort_key_value=None, 
                            **filter_expression_values):
        # Initialize DynamoDB resource
        
        table = DBManager.dynamodb.Table(table_name)

        # Initialize expression attribute values dictionary
        expression_attribute_values = {}

        # Build KeyConditionExpression based on partition key and sort key (if provided)
        key_condition_expression = None
        if partition_key_name and partition_key_value:
            key_condition_expression = f'{partition_key_name} = :pk'
            expression_attribute_values[':pk'] = partition_key_value
            if sort_key_name and sort_key_value:
                key_condition_expression += f' and {sort_key_name} = :sk'
                expression_attribute_values[':sk'] = sort_key_value
        else:
            if sort_key_name and sort_key_value:
                key_condition_expression = f'{sort_key_name} = :sk'
                expression_attribute_values[':sk'] = sort_key_value

        # Initialize query parameters dictionary
        query_params = {}

        # Add KeyConditionExpression if it's not None
        if key_condition_expression:
            query_params['KeyConditionExpression'] = key_condition_expression

        # Add FilterExpression if provided
        if filter_expression:
            query_params['FilterExpression'] = filter_expression
            # Dynamically add ExpressionAttributeValues for filter expression
            for key, value in filter_expression_values.items():
                expression_attribute_values[f':{key}'] = value

        # Add ProjectionExpression if provided
        if projection_expression:
            query_params['ProjectionExpression'] = projection_expression

        # Add IndexName if provided
        if index_name:
            query_params['IndexName'] = index_name

        # Add ExpressionAttributeValues
        query_params['ExpressionAttributeValues'] = expression_attribute_values

        # Perform the query
        # print (query_params)
        response = table.query(**query_params)

        return response['Items'] if 'Items' in response else None


    @staticmethod
    def getDBItemByPartitionKey(tableName, columnName, columnValue):
        
        try:
            
            table = DBManager.dynamodb.Table(tableName)

            response = table.query(
                            KeyConditionExpression=Key(columnName).eq(columnValue) 
                        )
            #print(response)
            return response['Items'][0] if 'Items' in response and len(response['Items']) > 0 else None
        
        except Exception as e:
            logging.error("Error occured in getDBItemByPartitionKey method: " + str(e))
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
    