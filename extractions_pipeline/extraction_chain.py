
from langchain.chains import TransformChain
from langchain.output_parsers import OutputFixingParser, PydanticOutputParser
from langchain.prompts import PromptTemplate
from extractions_pipeline.prompt_templates import fix_prompt_template
from extractions_pipeline.gpt_api import chat_completion

from extractions_pipeline.data_models import Transports
from extractions_pipeline.prompt_templates import transport_template




def fix_chain_fun(inputs):
        fix_prompt = PromptTemplate.from_template(fix_prompt_template)
        fix_prompt_str = fix_prompt.invoke({'instructions':inputs['instructions'],
                                            'completion':inputs['completion'],
                                            'error':inputs['error']}).text
    
        completion = chat_completion(fix_prompt_str)
    
        return {"completion": completion}



def extraction_chain(input, data_model = Transports, prompt_template = transport_template):

    fix_chain = TransformChain(
    input_variables=["instructions", "completion", "error"], output_variables=["completion"], transform=fix_chain_fun
    )  

    parser = PydanticOutputParser(pydantic_object=data_model)
    fix_parser = OutputFixingParser(parser=parser, retry_chain=fix_chain, max_retries=1)


    prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["input"],
        partial_variables={"format_instructions": parser.get_format_instructions()})
        

    prompt_str = prompt.invoke({"input":input}).to_string()

    response = chat_completion(prompt_str)
    return fix_parser.invoke(response).dict()


