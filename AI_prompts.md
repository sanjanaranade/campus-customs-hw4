# Campus Customs — Vibe Coder Prompt Log

This file records the prompts and instructions used while building the HW 4 Campus Customs project. Add each prompt as it is sent to the Vibe Coder, preserving the original wording whenever possible.

## Project context

- Store: Campus Customs, continuing the HW 3 project
- Frontend: React + Vite + TypeScript
- Backend: Python + FastAPI
- Agent: PydanticAI
- Data source: local `campus_customs.db`
- Public release: the finished project will be pushed to a public GitHub repository and submitted through Canvas
- Secrets: use the `PORTKEY_API_KEY` from the root `AI for Managers/.env`; never commit or expose it
- Model family: GPT-5.6 or GPT-6, using a stronger model for harder tasks when appropriate

## Problem 1 — Vibe Coder Prompts

### Initial prompt

> Please go ahead and create `AI_prompts.md` for me and make sure to keep it thoroughly updated as I work. This should be a log of everything I'm typing into my Vibe Coder.

### Follow-up prompts

The live site testing and app-check follow-up is recorded below.

### Why follow-up prompts were needed

No follow-up prompt was needed for this problem at the time of writing.

### Context and requirements established before Problem 1

These instructions establish the project context that future prompts in this log should be interpreted against:

- The project is the same Campus Customs store from HW 3.
- The website will use a React + Vite + TypeScript frontend, a Python + FastAPI backend, and a PydanticAI agent.
- Shoppers must be able to browse products, create an account, chat about merchandise, see matching product cards, and get honest price and stock answers from the local database.
- Product image paths are stored in the catalogue table, and the visual style and store information should be researched from `yalebulldogblue.com` for the agent prompt.
- The local data includes `campus_customs.db`, catalogue images, catalogue products, inventory by size, users with hashed passwords, and chat messages.
- AI calls must use the Portkey API key from the root `AI for Managers/.env`; secrets must never be logged or committed.
- Use an appropriate GPT-5.6 or GPT-6-series model, with a stronger model for harder tasks when useful.
- The completed project will be pushed to a public GitHub repository and submitted to Canvas by URL.

## Future problem sections

## Problem 2 — Analyze the Database

### Initial prompt

> Analyze the Database. Here, please examine closely the database `data/campus_customs.db` to make sure you grasp all the fields in the table. Understand `catalogue`, `inventory`, and `users` well.

### Follow-up prompts

None yet.

### Why follow-up prompts were needed

No follow-up prompt was needed for this problem. The database was available in the HW 4 folder as `campus_customs.db` rather than under a `data/` subfolder.

### Analysis outcome

- `catalogue` contains 102 products. Its fields are `product_id` (text primary key), `name`, `garment_type`, `description`, `colors`, `search_tags`, `image_file_path`, and `price`. The `colors` and `search_tags` values are JSON arrays stored as text. Image paths use the `products/<filename>.jpg` convention. Prices range from $32 to $98.
- `inventory` contains 612 records: one row for each product-size combination. Its fields are `id` (integer primary key), `product_id`, `size`, and `quantity`. `product_id` references `catalogue.product_id`, and `(product_id, size)` is unique. The six sizes are XS, S, M, L, XL, and XXL. Quantities range from 0 to 25, so zero means that size is currently out of stock; total stock must be calculated by summing sizes.
- `users` contains 3 accounts. Its fields are `id`, `name`, unique `email`, `password_hash`, `created_at`, `first_name`, and `last_name`. Passwords are stored as hashes and must never be exposed. The optional first/last-name columns are populated in the current data.
- The database also contains `chat_messages`, which has 22 existing records. Its fields are `id`, `user_id`, `role`, `content`, `products_json`, and `created_at`; `user_id` references `users.id`, and `products_json` stores matched-product data as JSON text.
- Integrity checks found no orphan inventory rows, duplicate product-size keys, negative quantities, missing required catalogue fields, users missing names, or chat messages pointing to nonexistent users.
- The database schema does not declare foreign-key enforcement or additional indexes beyond primary-key/unique indexes; backend queries should still use the documented relationships and validate inputs.

### Follow-up prompt: Database harness

> Given you understand the database well, begin the file `output/harness.md`. Jot down each table along with its fields, and briefly explain the importance/relevance of each field for the chatbot/shop. We will continue to grow this harness file throughout the project.

### Why this follow-up was needed

This follow-up was needed to turn the database analysis into a persistent, growing reference file for the chatbot and shop implementation.

## Problem 3 — Build the Campus Customs Website

### Initial prompt

> On to #3: Build the Campus Customs Website.

### Follow-up prompts

None yet. The user clarified that this problem title should be logged but that implementation should not begin yet.

### Why follow-up prompts were needed

No follow-up prompt was needed. The clarification was a correction to the implementation timing, not an additional website requirement.

### Follow-up prompt: frontend scaffold

> Let's start 3 for real now. Please scaffold a React Vite TypeScript front end for the Campus Customs website. Put a navigation bar at the top that links to the main pages, which are home, products, about us, log in, and create account. Examine and pull wording that is like the Campus Customs site from yalebulldogblue.com for the home and about sections, but do not copy the original text; put everything in your own voice and words.

### Why this follow-up was needed

This follow-up provided the first concrete implementation scope for Problem 3: the frontend technology, required navigation destinations, and the research-based but original copy direction for the Home and About sections.

### Follow-up prompt: catalogue product cards and detail pages

> On the Products page, show product images from the catalogue using the image paths from the database. Include basic product information such as name, price, and a brief description. Each product should open a single-item page with a large image on one side and full product text on the other, including description, price, stock, and sizes when available. When a shopper clicks a card on the Products page, take them to that page.

### Why this follow-up was needed

This follow-up expanded the initial visual scaffold into a catalogue browsing experience and specified the interaction between product cards and detail pages, including the database-backed stock and size information shoppers need before purchasing.

### Follow-up prompt: floating chat stub

> Continuing on Problem 3, add a floating chat panel interface in the bottom right of the site. It is okay that it does not speak with an agent yet. A stub that can communicate and call the backend later is good for now.

### Why this follow-up was needed

This follow-up added the shopper-facing chat entry point while intentionally deferring the PydanticAI connection. The interface needs to establish the future backend boundary without blocking the frontend build.

### Follow-up prompt: initial FastAPI API

> We will need a small API shortly so the database can be read. Start a simple FastAPI app in `backend/main.py` to serve products and images, and then we will grow it later.

### Why this follow-up was needed

This follow-up introduced the first backend boundary for the frontend. A small read-only API is needed to expose catalogue data, size-level inventory, and product images before authentication and the PydanticAI agent are added.

### Research and implementation note

The reference site was reviewed for high-level themes including Yale merchandise, campus pride, apparel and gifts, and a polished navy-and-white collegiate retail presentation. The scaffold uses those themes as inspiration while writing original Campus Customs copy.

## Problem 4 — Create Account & Login

### Initial prompt

> Let's do #4 now. It's called Create Account & Login. Create a normal create-account and login flow. Create account: first name, last name, password, and confirm password. Log in: email and password. Make sure that a new account is entered in the `users` table. Ensure that passwords are stored very securely so hackers can't see, use, or access them.

### Follow-up prompts

None yet.

### Why follow-up prompts were needed

No follow-up prompt was needed. The requirements were complete enough to implement the registration and login flow.

### Security implementation notes

- Passwords are hashed with Argon2 through `pwdlib` before insertion into `users`.
- Password confirmation is checked in the frontend before registration.
- The backend validates password length, normalizes email addresses, rejects duplicate accounts, and verifies hashes during login.
- API responses return safe public user fields only; `password_hash` is never returned.

### Follow-up prompt: verify seed and new accounts

> The seed database already contained a test user: `test@campuscustoms.yale.edu` with password `password`. Confirm that those credentials work and that a brand-new account also works as expected. If everything works, briefly update `output/harness.md` with how authorization works, what is stored for a user, and the elements used for secure password protection.

### Why this follow-up was needed

This follow-up required end-to-end verification against the supplied seed account and a newly inserted account, plus documentation of the final authentication behavior and security controls in the project harness.

### Verification result

The supplied seed login succeeded. A new verification account was inserted into `users` and logged in successfully. Neither successful response exposed `password_hash`. The seed database’s legacy PBKDF2 format is supported for compatibility, while new accounts use Argon2.

For every new problem, use this exact structure:

### Problem N — [Title]

#### Initial prompt

Record the user's original prompt verbatim whenever possible.

#### Follow-up prompts

Record every follow-up prompt verbatim, in chronological order. If there are no follow-ups, write “None yet.”

#### Why follow-up prompts were needed

For each follow-up, explain in one or more complete sentences what ambiguity, missing requirement, correction, or implementation issue made it necessary. If there were no follow-ups, explicitly say so.

## Maintenance notes

## Problem 5 — PydanticAI Agent Backend

### Initial prompt

> Problem 5 is called “PydanticAI Agent Backend.”

### Follow-up prompts

None yet.

### Why follow-up prompts were needed

No follow-up prompt was needed. This entry records the problem title only; implementation has not begun.

### Follow-up prompt: PydanticAI shop agent backend

> Build the shop chatbot as a PydanticAI agent behind FastAPI and plug it into the frontend widget. Keep `backend/main.py` as the Uvicorn app, with `backend/prompts/prompt.md` as the growing system prompt, `backend/agent.py` for agent entry and wiring, `backend/tools.py` for tools, and `backend/models.py` for structured types. Expose a chat route that returns an agent reply, and add whatever is needed for products and authorization. Use the Portkey model API key from the project environment.

### Why this follow-up was needed

This follow-up defined the Problem 5 architecture: the four-file PydanticAI split, FastAPI chat endpoint, frontend connection, database-backed tools, structured responses, and secret model-key handling.

### Implementation status

Implemented and compile-checked. The frontend widget now calls `POST /api/chat`; the backend loads `PORTKEY_API_KEY` from `AI for Managers/.env`, exposes catalogue tools, and returns structured replies with matching product cards. A live model call still requires the local key and network access.

### Follow-up prompt: agent voice, safety, models, harness, and launch command

> Put Campus Customs voice and safety basics into `backend/prompts/prompt.md`. Start or update types in `models.py` for chat replies and product cards as needed. Update `output/harness.md` with how the frontend talks to FastAPI and how the agent is loaded, including its file and model. Launch the backend from `backend/` with `uvicorn main:app --reload --port 8000`.

### Why this follow-up was needed

This follow-up added the agent’s behavioral guardrails, clarified the structured response contract, documented the frontend/API/model flow, and required verification using the exact Uvicorn launch pattern intended for development.

## Problem 6 — Tools: Product Info and Stock

### Initial prompt

> Let's do #6 now. It is called “Tools: Product Info and Stock.”

### Follow-up prompts

None yet.

### Why follow-up prompts were needed

No follow-up prompt was needed. This entry records the Problem 6 title; implementation requirements have not yet been provided.

### Follow-up prompt: database-backed product and stock tools

> Give the agent tools that look up real information from `campus_customs.db`, including product description, price, and how many are left in stock by size. The agent must use the database, not make up fake information. If something is not in stock or a size is unavailable, say exactly that.

### Why this follow-up was needed

This follow-up specified the required tool behavior and accuracy boundary for Problem 6: every product fact must come from SQLite, and size-level stockouts must be communicated explicitly.

### Follow-up prompt: explicit price and stock tool use

> Expand `prompts/prompt.md` so the agent knows to call the tools for questions related to price or stock. Add or update those return types in `models.py`. In `output/harness.md`, list each tool and briefly explain the search-result fields selected and why.

### Why this follow-up was needed

This follow-up made tool use mandatory for price and availability questions, formalized the structured lookup result, and documented the search-field design so future agent and API changes preserve database-grounded answers.

## Problem 7 — Chat Search that Updates the Page

### Initial prompt

> Excellent, that's it for Problem 6. Let's go on to Problem 7: “Chat Search that Updates the Page.”

### Follow-up prompts

None yet.

### Why follow-up prompts were needed

No follow-up prompt was needed. This entry records the Problem 7 title; implementation requirements have not yet been provided.

### Follow-up prompt: chat search updates the page

> Add a Campus Customs feature where a shopper can ask about a particular item, such as the kinds of hoodies available. The agent should search the catalogue and the site should dynamically show those items as product cards containing image, name, price, and short information. This is the API contract.

### Why this follow-up was needed

This follow-up defined the end-to-end chat-search contract: natural-language input, agent catalogue search, structured product results, and dynamic page updates with clickable product cards.

### Follow-up prompt: preserve single-item page behavior

> Make sure the HW 3 single-item page behavior still functions. Every product card, including cards brought up by chat, must open the detail view when clicked. Update `prompts/prompt.md` and `output/harness.md` to explain how search results reach the page.

### Why this follow-up was needed

This follow-up protected the existing HW 3 navigation behavior while adding chat-driven results, requiring every product-card source to share one detail-page click path and documenting that API-to-page flow.

## Problem 8 — Customer Memory

### Initial prompt

> Problem 8 is called “Customer Memory.”

### Follow-up prompts

None yet.

### Why follow-up prompts were needed

No follow-up prompt was needed. This entry records the Problem 8 title; implementation requirements have not yet been provided.

### Follow-up prompt: customer memory and contextual agent dependencies

> When a shopper is logged in, save their chat history in the database and reload it when they return to the chat. The agent must know who is talking, including name and email, through agent dependencies and callable tools. Pass enough overarching page context so broad questions such as “do we have this in stock in blue?” can be understood while the shopper browses.

### Why this follow-up was needed

This follow-up defined persistent chat memory, authenticated shopper identity, dependency-injected agent context, a context tool, and page-aware interpretation for follow-up product questions.

### Follow-up prompt: guest chat without saved history

> Guests should still be able to chat, but guest history does not need to be saved. Clearly and concisely document in `output/harness.md` how chat history is stored, which customer fields the agent can access, and how page context is transferred.

### Why this follow-up was needed

This follow-up clarified the privacy boundary between authenticated and guest chat and required a concise record of storage, agent dependencies, and frontend page-context transfer.

## Problem 9 — Usability Improvements

### Initial prompt

> Problem 9 is called “Usability Improvements.”

### Follow-up prompts

> Improve the core shop with two frontend usability improvements and two agent/backend usability improvements. Frontend: create clear filters and a Quick view product modal. Backend: create an inventory summary and bulk product updates such as selecting multiple products and placing a discount on all of them. Also write `output/usability.md`, describing what was added and why each touch helps the shopper or business, and double-check that all four appear and work.

### Why follow-up prompts were needed

This follow-up defined the four Problem 9 deliverables and required a dedicated usability record plus verification that each frontend and backend improvement remained integrated with the existing shop.

## Problem 10 — Style the Website

### Initial prompt

> Problem 10 is called “Style the Website.” Make the website look legit and real with cute elements: a varsity-letter-style header, Yale-inspired cream and navy colors, a pawprint cursor, icons, dog-like chat voice, cute handsome-Dan-inspired icons in the header and overall site, while keeping it accessible and readable.

### Follow-up prompts

> can you edit it to make the header move down so it doesn't overlap with the logo and add more faint paw prints all over it and also crete the cartoon handsome dan for the header too! maybe like wearing a cute backpack

> can you make him look more mascot-y and give him a cute backpack that's blue and overall make him look like a school gong dog

> no like make him wearing it on his back

> and make the pawprints in teh header bigger much bigger and like spread out

> pawprints MUCH Larger also make the cursor have blue glitter too as it moves if u can

> make the backpack look less liek a collar and liek a good backpack and make the pawprint logo like 10 x the size lol

> why is his ear detached

> have it connect to the top of his head so it like matches the left ear

> no they dont just pls fix it once and do it right

> please summarize briefly in output/design.md the changes i asked for and made clearly and why they would be beneficial for the customer in #10

> no like make him wearing it on his back

### Why follow-up prompts were needed

This follow-up was needed to correct the header's vertical spacing and prevent the decorative elements from competing with the wordmark. It also added a denser but intentionally faint paw-print pattern and a CSS-native cartoon Handsome Dan-inspired mascot with a backpack, while preserving the readable and accessible styling direction.

This follow-up was needed to refine the mascot's character and align its school-spirit details with the Yale-inspired palette. The mascot is now a fuller cartoon figure with a body, collar, expressive eyes, and a navy-blue backpack with a gold accent.

This follow-up was needed because the backpack previously read as a side accessory. It is now layered behind the body with visible shoulder-strap styling so Dan clearly appears to be wearing it on his back.

This repeated clarification indicated that the previous silhouette still was not visually clear enough. The backpack is now larger, placed behind the torso, and paired with two visible front shoulder straps and a top handle.

This follow-up was needed to make the paw-print decoration more visible and balanced across the full header. The prints were enlarged and redistributed from the left edge through the right edge while keeping their opacity low for readability.

This follow-up was needed to increase the decorative scale once more and add a playful cursor treatment. The header paws are now substantially larger, and mouse movement creates short-lived blue sparkle marks; the effect ignores touch pointers and is disabled when reduced motion is preferred.

This follow-up was needed because the backpack silhouette still resembled a collar at the mascot's small scale. The bag now has a larger blue body, top handle, flap treatment, and front pocket, while the pawprint logo is dramatically enlarged and the header is given extra vertical room.

This follow-up was needed to correct the mascot silhouette: the ears were positioned too far outward and appeared detached from the head. They now overlap the face more naturally and sit behind its outline so both ears visibly connect.

This follow-up was needed to make the ear attachment symmetrical. Both ears now begin at the top of the head and tuck behind the face outline, matching the left-ear connection.

This correction was needed because positioning the ears as separate mascot siblings still allowed a visible gap. Both ears are now nested inside the head element and anchored with negative top/side offsets, making the connection structural rather than approximate.

This follow-up was needed to create a concise customer-centered design record for Problem 10. It captures the requested styling changes, the mascot and interaction refinements, and the usability or brand benefit of each change.

## Problem 11 — Site testing (app check)

### Initial prompt

> Site testing (app check) is the name

### Follow-up prompts

The live site testing and app-check follow-up is recorded below.

### Why follow-up prompts were needed

The testing requirements are recorded in the follow-up section below.

### Follow-up prompt: live site testing and app check documentation

> For this one, you need to test the live site and also document it then in `output/app_check.html`. This should be a website that a user is able to double tap and click. In doing this, please ensure that you include screenshots and brief captions. These should be for the following: chat checking the inventory level of an item that is the honest stock/price from the DB, the dynamic search-result cards that appear after a question on a category is asked for example hoodies, and a usability feature from Problem 9!

### Why follow-up prompts were needed

This follow-up defined the Problem 11 acceptance checks: live interaction, database-grounded chat facts, chat-driven category cards, a Problem 9 usability feature, screenshots, and brief captions in a standalone HTML report.

### Implementation and verification notes

The live check passed for the FastAPI health route, the database-backed Basic Hoodie Big Yale inventory response, six dynamic hoodie search cards, and the Problem 9 Quick View modal. Testing exposed and corrected plural category matching so a natural “hoodies” request finds the catalogue’s “hoodie” records. Screenshots and captions are in `output/app_check.html` with supporting files under `output/app_check_images/`.

### Follow-up prompt: grader-friendly app check layout

> continuing #11, please ensure that the html is easy to grade for my grader. this means there should be a heading for each check, a screenshot, a brief description of the screenshot. make sure the screenshot image files are in output/app_check_images/ and pls make sure to link to them from app_check.html, with relative paths.

### Why this follow-up was needed

This follow-up clarified the grading format and required a predictable image directory with relative links. The report has a heading, screenshot, and caption for each check; the three images are now in `output/app_check_images/` and linked as `app_check_images/...` from the HTML file.

### Follow-up prompt: confirm prompt logging

> great. also pls log everything as i am sure u r

### Why this follow-up was needed

This follow-up reaffirmed the requirement that every instruction and confirmation related to Problem 11 be preserved in the prompt log, including the grading-format update and its implementation status.

## Problem 12 — Audit trail, safety, finish harness

### Initial prompt

> let's do #12 now --- this is called Audit trail, safety, finish harness.

### Follow-up prompts

> Please maintain an append-only output/audit_trail.json file that has the agent loop activity, including time, tool name, short args/result, and stop reason. Please make sure you do NOT erase it in between different runs. Please also come up with thorough yet concise safety rules for the agent and place them inside prompts/prompt.md.

> ok just please make sure that the safety rules are in prompts/prompt.md!

### Why follow-up prompts were needed

The first follow-up defined persistent agent/tool observability, non-destructive audit retention, concise operational safety guardrails, and completion of the harness documentation. The second follow-up clarified the required destination for those safety rules: backend/prompts/prompt.md.

### Follow-up prompt: finish the harness specification

> Then, please finish output/harness.md so that we know clearly how the system is operating! This should include model fields in models.py as well as a brief explanation for why they were chosen, tools and abilities, safety rules we came up with, and detailed specifications including loop limits, models, result caps, and directions to run the front and back ends. Once you do all this, this wraps up #12! Make sure this is also all accurately logged, including follow-ups and everything.

> hurry

### Why this follow-up was needed

This follow-up completed the Problem 12 documentation requirement by making the harness a grader-ready operating specification. It required the model-field rationale, tool inventory, safety summary, actual loop/model/result limits, run commands, and a complete prompt history.

## Problem 13 — Push to GitHub and submit the URL

### Initial prompt

> finally we are now on the last one which is #13. this is called: push to github and submit the url. do not do anything yet but log the number and title etc in the log

### Follow-up prompts

> Great. Please put just the full code—making sure it's complete and has everything we just did for the site and stuff—and we need to push it to a public GitHub repository. I need to later be able to submit just the link to the repo URL. Do not place my real `.env` file, the real CC `.db`, or any product images in the repo. Please use `.gitignore` and include `.env.example` with placeholders only. Here is the expected file layout my professor expects: within `hw4/`, `AI_prompts.md`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md`, `frontend/` containing the Vite React TypeScript app, `backend/` containing `main.py`, `agent.py`, `models.py`, `tools.py`, and `prompts/prompt.md`, and `output/` containing `harness.md`, `design.md`, `usability.md`, `app_check.html`, `app_check_images/` with the screenshots, and `audit_trail.json`. The local-only data pack must remain outside Git: `data/campus_customs.db` and `data/products/` with the catalogue images. The agent should remain the four requested files under `backend/`: `agent.py`, `prompts/prompt.md`, `tools.py`, and `models.py`; `main.py` is the FastAPI entry point. Finally, `README.md` must explain how to run both front and back ends after placing the data pack.

### Why follow-up prompts were needed

This follow-up defined the Problem 13 packaging contract, the public-repository goal, the exact grader-facing layout, the required local-only data and secret exclusions, the environment template, and the run instructions that must be documented before any push.

### Follow-up prompt: creating the public repository

> wait i think i have a github what do u need from me

> how do i do that

### Why follow-up prompts were needed

These follow-ups clarified what repository information is needed to publish the finished project and requested beginner-friendly instructions for locating or creating an empty public GitHub repository without sharing a password or access token.

### Follow-up prompt: repository URL supplied

> i think i did all that. is that what u need [https://github.com/sanjanaranade/campus-customs-hw4.git](https://github.com/sanjanaranade/campus-customs-hw4.git)

### Why this follow-up was needed

This follow-up supplied the exact public GitHub remote needed to publish the verified local `main` branch.

### Follow-up prompt: request to run the push

> can u run that in my terminal

### Why this follow-up was needed

This follow-up authorized running the prepared Git push from the project terminal, subject to the user's local GitHub authentication and without transmitting credentials in chat.

### Follow-up prompt: locating the terminal

> where is my vs code terminal window

### Why this follow-up was needed

This follow-up requested basic navigation help so the user could run the authenticated Git push locally without sharing credentials.

### Follow-up prompt: confirm push completion

> done? i think

### Why this follow-up was needed

This follow-up requested verification that the authenticated push completed successfully and that the local repository remained intact.

### Follow-up prompt: opening the website

> great! but like how do i see the website lol

### Why this follow-up was needed

This follow-up requested the local development commands and browser address needed to view the completed frontend with its FastAPI backend.

### Follow-up prompt: submission clarification

> so what do i submit im so confused

### Why this follow-up was needed

This follow-up requested a clear distinction between the local development address and the public GitHub repository URL required for the Canvas submission.

### Follow-up prompt: repository versus live website

> so what i submit does NOT lead to the direct website i made tho

### Why this follow-up was needed

This follow-up identified the difference between a public source-code repository and a separately deployed live website, so the submission guidance could be made explicit.

### Follow-up prompt: Canvas clone-link requirement

> ok the canvas instructions say "on canvas, submit the repo url which is teh link that ur graders can open and clone"

### Why this follow-up was needed

This follow-up confirmed that the required submission is the public repository URL, which graders can open and clone, rather than a separately hosted website URL.

### Follow-up prompt: what graders see in a browser

> but of tjeu open it in a browser they cant see my actual site right

### Why this follow-up was needed

This follow-up clarified that opening a GitHub repository displays the source and documentation, while viewing the interactive app requires running the frontend/backend with the local data pack or separately deploying the application.

### Follow-up prompt: submission link and local preview

> ok so one more time can u give me both the link i need to submit as well as the final website just so i can see how cute it is

### Why this follow-up was needed

This follow-up requested both final destinations: the public repository URL for Canvas and the local frontend URL for previewing the completed interactive design.

### Follow-up prompt: final Canvas URL confirmation

> confirming that THIS is the link i submit to canvas? [https://github.com/sanjanaranade/campus-customs-hw4](https://github.com/sanjanaranade/campus-customs-hw4)

### Why this follow-up was needed

This follow-up requested final confirmation of the exact public repository URL to submit for grading.

- Add new prompts chronologically under the appropriate section.
- Keep the original prompt text separate from implementation notes or results.
- Never combine prompts from different problems into one section.
- Record the problem number and title exactly as provided by the assignment when available.
- For every follow-up prompt, include the reason it was needed; do not leave this field blank.
- Never copy API keys, passwords, tokens, or other secrets into this file.
- When a prompt changes an earlier requirement, record the new prompt and note what it supersedes.
