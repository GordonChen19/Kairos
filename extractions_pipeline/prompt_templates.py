transport_template  = ''' 

You are a transport expert. You have been given a piece of text which states how a user gets from place A to place B via different modes of transportation. 
Your job is to convert the text into a structured series of chronological events. Each event contains the source and destination including the mode of transportaion to get between them.

Example Text:

From Bishan Sky Habitat to SAP, I take the bus to Bishan MRT station. From there, I take the MRT to Labrador Park. Finally, I walk the rest of my way there. 


Output:

1. 
      "source": "Bishan Sky Habitat",
      "destination": "Bishan MRT station",
      "transportationMode": "bus"

2.
      "source": "Bishan MRT station",
      "destination": "Labrador Park",
      "transportationMode": "subway"

3.
      "source": "Labrador Park",
      "destination": "SAP",
      "transportationMode": "walk"




You are to respond in the JSON format defined below.


Format Instructions:
--------------
{format_instructions}
--------------

Text:
--------------
{input}
--------------

'''


fix_prompt_template = """Instructions:
--------------
{instructions}
--------------
Completion:
--------------
{completion}
--------------

Above, the Completion did not satisfy the constraints given in the Instructions.
Malformed Error:
--------------
{error}
--------------

 
Please try again. Please only respond with an answer that satisfies the constraints laid out in the Instructions.
Important:  Only correct the structural issues within the JSON format. Do not modify the existing data values themselves:"""


