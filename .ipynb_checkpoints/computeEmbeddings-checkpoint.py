from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
import json as json

class ComputeEmbeddings():
    def __init__(self, inputFileName, outputFileName, tokenizer, model):
        self.inputFileName = inputFileName
        self.outputFileName = outputFileName
        
        # Load model from HuggingFace Hub
        self.tokenizer = tokenizer
        self.model = model

    #Encode text
    def encode(self, texts):
        # Tokenize sentences
        encoded_input = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')

        # Compute token embeddings
        with torch.no_grad():
            model_output = self.model(**encoded_input, return_dict=True)
        
        # Perform pooling
        embeddings = self.mean_pooling(model_output, encoded_input['attention_mask'])

        # Normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)
        
        return embeddings

        
    #Mean Pooling - Take average of all tokens
    def mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output.last_hidden_state #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

    def createMap(self):
        with open(self.inputFileName, "r") as read_file:
            recipes = json.load(read_file)

        embeddings = {}

        for recipeId in recipes:
            embeddings[recipeId]={}
            
            # Sentences we want sentence embeddings for
            # Title
            recipeTitle = recipes[recipeId]['recipe']['displayName']
            title_emb = self.encode(recipeTitle)
            embeddings[recipeId]["title_embedding"] = title_emb[0].numpy().tolist()

            # Description
            if recipes[recipeId]['recipe']['description'] != None :
                recipeDescription = recipes[recipeId]['recipe']['description']
                description_emb = self.encode(recipeDescription)
                embeddings[recipeId]["description_embedding"] = description_emb[0].numpy().tolist()
            else:
                recipeDescription = recipes[recipeId]['recipe']['displayName']
                embeddings[recipeId]["description_embedding"] = title_emb[0].numpy().tolist()

            
        # Write to file
        f = open(self.outputFileName, 'w')
        f.write(json.dumps(embeddings))

        return
    
    





