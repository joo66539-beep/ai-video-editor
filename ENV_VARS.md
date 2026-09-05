# How to set the OPENAI_API_KEY on Render

1. Go to your Render service > Settings > Environment.
2. Click "Add Environment Variable" and add a variable named OPENAI_API_KEY with the value of your OpenAI secret key.
3. Deploy or Redeploy the service.

# How to add the variable in Vercel

1. Go to your Vercel project > Settings > Environment Variables.
2. Add NEXT_PUBLIC_API_URL with the backend URL (from Render), for the Environment: Production (and Preview if you like).
3. Redeploy the frontend after adding the variable.
