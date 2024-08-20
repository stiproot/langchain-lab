
from langchain_openai import AzureChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate

from common.model_factory import ModelFactory

summarization_model = ModelFactory.create()

translation_model = ModelFactory.create()

def chain_models(input_text):
    summarization_system_message = ("system", "You are a helpful assistant that summarizes text concisely.")
    translation_system_message = ("system", "You are a helpful assistant that translates text to French.")

    human_message = ("human", "{input_text}")

    result = (
        ChatPromptTemplate.from_messages([summarization_system_message, human_message])
        | summarization_model 
        | (lambda x: translation_system_message + ("human", x.content))
        | translation_model
        | StrOutputParser()
    )

    return result.invoke({"input_text": input_text})

input_text = """Butterflies are winged insects from the lepidopteran suborder Rhopalocera, characterized by large, often brightly coloured wings that often fold together when at rest, and a conspicuous, fluttering flight. The group comprises the superfamilies Hedyloidea (moth-butterflies in the Americas) and Papilionoidea (all others). The oldest butterfly fossils have been dated to the Paleocene, about 56 million years ago, though they likely originated in the Late Cretaceous, about 101 million years ago.[1]

Butterflies have a four-stage life cycle, and like other holometabolous insects they undergo complete metamorphosis.[2] Winged adults lay eggs on the food plant on which their larvae, known as caterpillars, will feed. The caterpillars grow, sometimes very rapidly, and when fully developed, pupate in a chrysalis. When metamorphosis is complete, the pupal skin splits, the adult insect climbs out, expands its wings to dry, and flies off.

Some butterflies, especially in the tropics, have several generations in a year, while others have a single generation, and a few in cold locations may take several years to pass through their entire life cycle.[3]

Butterflies are often polymorphic, and many species make use of camouflage, mimicry, and aposematism to evade their predators.[4] Some, like the monarch and the painted lady, migrate over long distances. Many butterflies are attacked by parasites or parasitoids, including wasps, protozoans, flies, and other invertebrates, or are preyed upon by other organisms. Some species are pests because in their larval stages they can damage domestic crops or trees; other species are agents of pollination of some plants. Larvae of a few butterflies (e.g., harvesters) eat harmful insects, and a few are predators of ants, while others live as mutualists in association with ants. Culturally, butterflies are a popular motif in the visual and literary arts. The Smithsonian Institution says "butterflies are certainly one of the most appealing creatures in nature".[5]
"""
result = chain_models(input_text)
print(result)
