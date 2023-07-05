#Generates prompt for Open AI input.
def retPrompt(reviewStr):
#Please note any and all changes to this prompt are highl destructive and can affect
#functionality across the board for all OpenAI related scripts.
    prompt = f"""
            
            Read the app review below denoted with <>.
            <{reviewStr}>
            
			Based on the content of the review, determine if the concepts denoted below with ~~ are present in
            the review. The definitions, denoted with ~~, are composed of a hierarchical list of primary dimensions, 
            each followed by a subservient list of sub-dimensions.
            ~{definition}~

            For each of the dimensions and their sub dimensions, if they are present within the review, give a score of true.
            If they are NOT present within the review, give a score of false.
            
            
            Use the following json file format for your response:
            {jsonFormat}		

            Fill in the "Strongest Sub-Dimension" schema with the sub-dimension that is mentioned first in the review denoted with <>.
            Fill in the "Strongest Sub-Dimension Definition" schema with the corresponding defintion.

            Return only the json format.
            """
    return prompt

jsonFormat="""
{
	"Content" : "empty",
	"ID" : "empty",
	"App Name" : "empty",
	"Strongest Sub-Dimension": Sub-Dimension Here,
	"Strongest Sub-Dimension Definition" : Sub-Dimension Definition Here,
	"Transparent Interaction" : True/False,
	"Transparent Interaction Sub-Dimensions" : [
	{
		"Activation" : True/False,
    	"Saliency" : True/False,
		"Usability" : True/False,
		"Deep Trust" : True/False
    }
	]
}
  	]
	"Representational Fidelity" : True/False,
  	"Representational Fidelity Sub-Dimensions" : [
    {
		"Currency" : True/False,
		"Completeness" : True/False,
		"Exactitude" : True/False,
		"Consistency" : True/False,
		"Relevance" : True/False,
		"Representational Trust" : True/False
    }
  	]
	"Situational Awareness" : True/False,
  	"Situational Awareness Sub-Dimensions": [
	{
		"Promptness" : True/False,
		"Actionability" : True/False,
		"Situational Trust" : True/False
	}
    ]
}


"""


definition=[
	{
  	"Dimension": "Transparent Interaction",
  	"Definition": "Is the extent to which users can easily access and interact with the app without any obstacles.",
  	"Sub-Dimensions": [
    	{
      	"Sub-Dimension": "Activation",
      	"Definition": "The app's ability to quickly alert users when they receive an emergency notification."
    	},
    	{
      	"Sub-Dimension": "Saliency",
      	"Definition": "The app's ability to alert users based on the type and severity of the emergency."
    	},
    	{	
      	"Sub-Dimension": "Usability",
      	"Definition": "The app is ease to use, accessible, and respond quickly when the users interacts with it."
    	},
    	{
      	"Sub-Dimension": "Deep Trust",
      	"Definition": "Users' confidence in the app's underlying structure, such as its codebase, ensuring no privacy violations or tracking."
    	}
  	]
	},
	{
  	"Dimension": "Representational Fidelity",
  	"Definition": "The extent to which notifications accurately represent emergencies to users.",
  	"Sub-Dimensions": [
    	{
      	"Sub-Dimension": "Currency",
      	"Definition": "Providing users with up-to-date information about emergencies and the actions to take."
    	},
    	{
      	"Sub-Dimension": "Completeness",
      	"Definition": "Ensuring users have a comprehensive representation of emergencies and the necessary counteractions."
    	},
    	{
      	"Sub-Dimension": "Exactitude",
      	"Definition": "Delivering correct and precise information about emergencies and the corresponding actions to take."
    	},
    	{
      	"Sub-Dimension": "Consistency",
      	"Definition": "Maintaining coherence in the representations of emergencies and the recommended counteractions."
    	},
    	{
      	"Sub-Dimension": "Relevance",
      	"Definition": "Providing users with representations of non-trivial emergencies that pose immediate threats."
    	},
    	{
      	"Sub-Dimension": "Representational Trust",
      	"Definition": "Building users' confidence in the accuracy of representations and the effectiveness of the suggested counteractions."
    	}
  	]
	},
	{
  	"Dimension": "Situational Awareness",
  	"Definition": "The extent to which information in the alert message enables users to take effective actions.",
  	"Sub-Dimensions": [
    	{
      	"Sub-Dimension": "Promptness",
      	"Definition": "Enabling users to quickly take protective actions based on the provided information."
    	},
    	{
      	"Sub-Dimension": "Actionability",
      	"Definition": "Offering users actionable recommendations to respond to emergencies in their environment."
    	},
    	{
      	"Sub-Dimension": "Situational Trust",
      	"Definition": "Instilling in users the belief that they can effectively carry out projected actions by relying on the information from the emergency notification."
    	}
  	]
	}
  ]