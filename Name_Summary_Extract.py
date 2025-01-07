import getpass
import os
from langchain_groq import ChatGroq
os.environ["GROQ_API_KEY"] = ""
llm = ChatGroq(model="llama3-8b-8192")

from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate


import ast

def name_extract(text, label):

    # Connect to SQLite database
    conn = sqlite3.connect('example.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Fetch all matching rows
    cursor.execute('SELECT * FROM data WHERE label = ?', (label,))
    rows = cursor.fetchall()

    examples = []
    for row in rows:
        examples.append({"input": f"label: {row['label']}, text: {row['text']}", "output": f"{{'Name': '{row['name']}', 'Address': '{row['address']}'}}"})

    # Close the connection
    conn.close()


     examples_manual = [
        {"input": "label: resume, text: '| [ . Adams Letter Co., Inc. 55 VANDAM STREET NEW YORK, N. Y, 10013 pave = HAKCH 29, 1972 TO LEONARD ZAHN ASSOCIATES P. 0. BOX $23 buat ers hi 13 LINCOLN Ride sii GREAT NECK, Ne Yo 11022 TERMe: WET 3D SSS COUNCIL FOR TORACCO RESEARCH EXHIBITION SET ALL COMPOSITION, SUoMIT PROOFS, MAKE CHANGES, ENLARGE ALL BLOCKS OF COPY APPROXIMATELY 300% = MAKE CONTACT PRINTS AND POSITIVES, $488.00 TAX 4 $522.36 POR IVEL CONSTRUCTION Aaa p 1'",
        "output": "{'Name': 'LEONARD ZAHN ASSOCIATES', 'Address': '55 VANDAM STREET NEW YORK, N. Y, 10013'}"},
        {"input": "label: Driving_License, text: CEADUNAS TIOMANA DRIVING LICENCE EIRE . orpaig| nonmode! IRELAND Chnawnozyoncyao 2a y 10 ACK A; Davenport oo. ene | ated, coi condoocion ~ | Gregory aoduocion tbhdiéosh: er iv fers ] da, 28.05.88 4C. MINISTRY. OF THE INTERIOR, 2 conde db, 19.11.82 4d. 084653924 oy)! iumnjo padpnajiovas 5. 87CDNO69CR yereebi ov Lloorigja tad-sowqor (;OOIOUS Heown jevdy SFU UI sla ae conadvucgon a. fe cond Mennis do condiscoce ' 8, 119 Dana Stravenue doolionjo Jj New Hampshire Lao People's Deiibera C)(& van 9. A2D1A1AMBI1C ae aiein Kovels nyqono Hezoils de",
        "output": "{'Name': 'Gregory Davenport', 'Address': '119 Dana Stravenue, New Hampshire Lao People\'s Democratic Republic'}"},
        {"input": 'label: Driving_License, text: Find name and address in the following: CEADUNAS TIOMANA DRIVING LICENCE EIRE ‘adan an Aontais Eorpoigh europecn Union mode! IRELAND ChnatnozonciAo 2a ynpcanoessno nerc 1, Ochoa iivicowa ounc Penniso de conduccion a Bobby nonduocion fhdiéshy prokaz tiaralcoct 3, 10.01.83 deer aptabae | — ciesla bales ) t } Jt / wa pee al ie €oOn 1O6 4a, 31.12.10 4c, NDLS OC lorie. di qolde Vaditaje apltocilea 4b, 09.07.72 4d. 196954042 onliocila Valiuninio painpnhjiovns 5. W2WVA00606 cane gcree Bete plea he LOY Gis POUT j OW) {OC Thu |): Cana de conducina Pennis do condiscoce icy peurshes yuk 487 Kristi Cove “Yoo 20 davialionjo Vermont Cambodia 51595° MOTETY HAISICOl 4NCTCNCTOO 9G YNIIME ; Onc1oCoOcO!LE Hidik 9, A1CA2B1D1 i tetachele Kerker IONYqQonO Hoezoale de coadoine',
        "output": "{'Name': 'Bobby Ochoa', 'Address': '487 Kristi Cove, Vermont, Cambodia, 51595'}"},
        {"input": 'label: invoice, text: her | LOUISE NORMAN Rede L PROJECT NO, —_SP. TRAVEL EXPENSES FOR VALERIE OBEN Markel | SVoOpaaion 3 1 PH RSIDE AVE., WESTPORT, CONN. 06880 (203) 222-1000 aa Pil "92 TANF 2086 , INVOIGE ” | SALES PROMOTION DIVISION | | 32364 | | | NUMBERS REYNOLDS 401 NORTH MAIN STREET DATE: 03/27/92 WINSTON~SALEM VNC 27102 _! CLIENT CODE NO. f . < ‘ ll gone . : pe “ n x - == . m (== 4 ‘ Wf Ari DESCRIPTION AMOUNT 1/29-31 AIRFARE CNYC~GSO-NYC) 564.007 LODGING 49 yr} 197.12°1 MEALS (3 DAYS) 59.00 MILEAGE 29464 MISC. CLIMCs/PARKINGsTAXI-TOLLS-TIPS) 93.00 | CC: DOUG MARTIN APPROVAL CONTRACT #200 O2, CHARGE Core Sipes RETUEN TQ LAN. . . | | | wn pa w iS) o NET 30 DAYS w © © > Mi O: PO 80x 9 5 ‘+ TOTAL DUE 5',
        "output": "{'Name': 'R. J. Reynolds', 'Address': '401 North Main Street, Winston-Salem'}"},
        {"input": 'label: balance_sheet, text: [Standalone (Rs. In Cr) [Consolidated (Rs. In Cr) Year En — bicaaeas Consolidated 31.03.2018 | cae Iecmzoss | 31.03.2017 [Audited [Audited AjAssets | |[Property, plant and equipment [2,486.37 [2,397.98 2,487.98 _|[2,399.99 [ [Capital work-in-progress (73.00 25.49 — |(73.00 [ [Investment property | | je.56 [8.56 [ [intangible assets 5.18 [1.07 (5.18 [ intangible assets under development 0.51 0.51 jo.s1 0.51 [ [Investment in subsidiaries [0.04 [0.04 [- - | [Financial assets | | | | | |[@ Investments 10.28 8.78 [| |[@i) Loans [p45 10.35 (6.81 [6.81 [ | (iii) Other non-current financial assets 4.81 8.25 [4 81 [8.25 | |[(iv) Other-non current assets [30.51 17.19 30.51 LI | | | |! | |Current assets | | [ [Inventories 587.88 (509.24 [636.70 (584.33 [ [Financial assets | | | [ss | |@ Trade receivables 285.56 (32685 22867  —|[276.16 [ \\[(i) Cash and cash equivalents [9.01 jp.14 11.58 (9.29 (iii) Bank balances other than cash and cash equivalents ‘15.23 26.85 - [ | (iv) Other current financial asset [10.72 ‘||19.26 |[e.82 [16.58 | [Current tax assets (net) (20.21 [41.89 20.21 [41.89 [ Other current assets [76.98 (68 84 [79.29 [71.86 ———EEEEEE&=_N | aa Assets 3,624.74 3,467.73 [3,628.14 —_3,503.60 LI ] 1 | B|Equity and Liabilities | i [_[Equity I | ] | [ [Equity share capital fo7.42 —fo9.47 _—iig7.42 (99.47 [ Other equity ‘524.52 [1,251.85 [1,513.42 as es es es [ [Liabilities | | | | [ |[Non-current liabilities | | | | [ [Financial liabilities | | | [fo Long term borrowings 744.33 (697.96 [744.33 697.96 [ [Long Term Provisions [6.33 (6.13 [6.33 | [Deferred tax liabilities (net) (194.95 235.98 —fie4.95 —_—‘if235.98 {fee aes fp [Current liabilities | | | {ss [ [Financial liabilities | | | | |@ Short term borrowings 30976 514.02 = [408.20 = Sa6.62_— | ||Gi) Trade payables (382.44 [333.74 = 382.44 —_—=|(333.73 | [Gi Other current financial liabilities 228.11 [298.29 | Other current liabilities fs1.80 13.60 ‘(37.86 21.61 | [Short term provisions 15.08 16.69 15.08 —— rs | Total Equity and Liabilities 3,624.74 [3,467.73 |3,628.14 [3,503.60',
        "output": "{'Name': None, 'Address': None}"}
    ]

    if len(examples) < 5: examples.extend(examples_manual)
    
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        # The list of examples available to select from.
        examples,
        # The embedding class used to produce embeddings which are used to measure semantic similarity.
        HuggingFaceEmbeddings(),
        # The VectorStore class that is used to store the embeddings and do a similarity search over.
        Chroma,
        # The number of examples to produce.
        k = 5,
    )

    # This is a prompt template used to format each individual example.
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=examples,
    )


    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Extract Name and Address if found as per examples."),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )

    chain = final_prompt | llm

    response = chain.invoke({"input": f"label: {label}, text: {text}"}).content
        try:
        name = ast.literal_eval(response)["Name"]
    except KeyError:
        name = 'None'

    try:
        address = ast.literal_eval(response)["Address"]
    except KeyError:
        address = 'None'

    return name, address

def summary_extract(label, text):

    response = llm.invoke(f"""Give summary in 2 lines: Document type: {label}, content: {text}. 
    Provide a concise overview capturing the document's 
    - main purpose
    - key details
    - significant insights
    tailored to the specific document type for clarity and relevance. 
    Only return the summary, don't add anything like 'here is a summary'""")
    
    return response.content

