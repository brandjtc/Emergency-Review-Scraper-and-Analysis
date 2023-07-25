#Generates prompt for Open AI input.
def retPrompt(reviewStr):
#Please note any and all changes to this prompt are highl destructive and can affect
#functionality across the board for all OpenAI related scripts.
    prompt = f"""
            
            Read the app review below denoted within <>.
            <{reviewStr}>
            
			Using the below definitions of constructs, denoted within ~~, 
            determine if any of the constructs is mentioned within the review.
            ~{definition}~

            If any of the constructs are mentioned within the review, regardless of their sentiment, assign to that construct a score of true.
            If a construct is not mentioned within the review, assign to that construct a score of false.
            
            
            Use the following json file format for your response:
            {jsonFormat}		

            Return only the json format.
            """
    return prompt

jsonFormat="""
{
	"Content" : "empty",
	"ID" : "empty",
	"App Name" : "empty",
	"Transparent Interaction" : True/False,
	"Transparent Interaction Sub-Dimensions" : [
	{
		"Activation" : True/False,
    	"Saliency" : True/False,
        "Autonomy" : True/False,
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
  	"Definition": "The extent to which users can easily access and interact with the app without any obstacles.",
  	"Sub-Dimensions of Transparent Interaction": [
    	{
      	"Sub-Dimension": "Activation",
      	"Definition": "the affordance to put the user in a state of alert within a useful timeframe upon receiving an emergency notification"
    	},
    	{
      	"Sub-Dimension": "Saliency",
      	"Definition": "the affordance to put the user in a state of alert that is congruent with the type of emergency and its severity."
    	},
        {
          "Sub-Dimension": "Autononmy",
          "Definition" : "is the affordance minimize the user’s intervention when configuring the apps by means of effective default settings upon installation"
		},
    	{	
      	"Sub-Dimension": "Usability",
      	"Definition": "is the affordance to enable the user to interact with the app easily"
    	},
    	{
      	"Sub-Dimension": "Deep Trust",
      	"Definition": "is the affordance to increase the user’s level of confidence that the application is designed to support only its intended use."
    	}
  	]
	},
	{
  	"Dimension": "Representational Fidelity",
  	"Definition": "The extent to which notifications accurately represent emergencies to users.",
  	"Sub-Dimensions": [
    	{
      	"Sub-Dimension": "Currency",
      	"Definition": "is the affordance to provide the user with up-to-date representations of the emergency and counteractions to take"
    	},
    	{
      	"Sub-Dimension": "Completeness",
      	"Definition": "is the affordance to provide a user with a comprehensive representation of the emergency and the counteractions to take"
		},
    	{
      	"Sub-Dimension": "Exactitude",
      	"Definition": "is the affordance to provide a user with a correct and precise representation of an emergency and adequate counteractions to cope with it."
    	},
    	{
      	"Sub-Dimension": "Consistency",
      	"Definition": "is the affordance to provide users with coherent and unequivocal representations of an emergency and the counteractions to take."
    	},
    	{
      	"Sub-Dimension": "Relevance",
      	"Definition": "is the affordance to provide users with representations of an emergency that is non-trivial or poses an immediate threat."
    	},
    	{
      	"Sub-Dimension": "Representational Trust",
      	"Definition": "is the affordance to increase the user’s level of confidence that representations of an emergency are accurate and that suggested counteractions will be effective"
    	}
  	]	
	},
	{
  	"Dimension": "Situational Awareness",
  	"Definition": "The extent to which information in the alert message enables users to take effective actions.",
  	"Sub-Dimensions": [
    	{
      	"Sub-Dimension": "Promptness",
      	"Definition": "is the affordance to enable a suer to quickly take protective actions."
    	},
    	{
      	"Sub-Dimension": "Actionability",
      	"Definition": "is the affordance to provide a user with recommendations for actions they can enact in their environment."
    	},
    	{
      	"Sub-Dimension": "Situational Trust",
      	"Definition": "is the affordance to increase the user’s level of confidence in their ability to carry out projected actions effectively by leveraging information in the emergency notification."
    	}
  	]
	}
  ]