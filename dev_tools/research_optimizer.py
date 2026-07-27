import itertools
import re
import time
from copy import deepcopy
from dataclasses import dataclass
from functools import wraps

import numpy as np
from numba import jit
from tqdm import tqdm
from tqdm.contrib.concurrent import process_map

"""
Hard-coded refresh weights and drop data
Historical drop-rate dataset snapshot: 2022-01-02, approximately 56,000 samples
Assume Research Series 2 and 3 are complete; transfer their targeted-project weight to Series 4
Assume Series 2 and 3 projects refresh like Series 4 but provide no useful rewards
"""
# Index, series, name, appearance weight, rainbow BP drops, rainbow BP drops, gold BP drops, gold BP drops, gold BP drops, rainbow gear drops
PROJECT_TABLE = """
0	4	B-4	58.42861987	0	0	0.346666667	0.346666667	0.346666667	0.0588
1	4	B-4	58.42861987	0	0	0.346666667	0.346666667	0.346666667	0.0588
2	4	B-4	58.42861987	0	0	0.346666667	0.346666667	0.346666667	0.0588
3	4	B-4	58.42861987	0	0	0.346666667	0.346666667	0.346666667	0.0588
4	4	B-4	58.42861987	0	0	0.346666667	0.346666667	0.346666667	0.0588
5	4	B-4	58.42861987	0	0	0.346666667	0.346666667	0.346666667	0.0588
6	4	B-4	58.42861987	0	0	0.346666667	0.346666667	0.346666667	0.0588
7	4	B-4	58.42861987	0	0	0.346666667	0.346666667	0.346666667	0.0588
8	4	B-4	58.42861987	0	0	0.346666667	0.346666667	0.346666667	0.0588
9	4	B-4	29.21430994	0	0	0.346666667	0.346666667	0.346666667	0.0588
10	4	B-4	29.21430994	0	0	0.346666667	0.346666667	0.346666667	0.0588
11	4	C-6	303.3660224	0	0	0	0	0	0.06
12	4	C-8	205.3100712	0.0645	0.0645	0.151	0.151	0.151	0.08
13	4	C-12	155.8916073	0.079	0.079	0.245333333	0.245333333	0.245333333	0.12
14	4	C-6	303.3660224	0	0	0	0	0	0.06
15	4	C-8	205.3100712	0.0645	0.0645	0.151	0.151	0.151	0.08
16	4	C-12	155.8916073	0.079	0.079	0.245333333	0.245333333	0.245333333	0.12
17	4	Agir-0.5	25.39955239	6	0	0	0	0	0.14
18	4	Agir-2.5	766.6697864	1.2	0	0	0	0	0.04
19	4	Agir-5	485.7871007	2.5	0	0	0	0	0.06
20	4	Agir-8	200.3313937	4	0	0	0	0	0.096
21	4	Hakuryu-0.5	25.39955239	0	6	0	0	0	0.14
22	4	Hakuryu-2.5	766.6697864	0	1.2	0	0	0	0.04
23	4	Hakuryu-5	485.7871007	0	2.5	0	0	0	0.06
24	4	Hakuryu-8	200.3313937	0	4	0	0	0	0.096
25	4	Anchorage-0.5	25.39955239	0	0	9	0	0	0.14
26	4	Anchorage-2.5	766.6697864	0	0	2.25	0	0	0.04
27	4	Anchorage-5	485.7871007	0	0	3.75	0	0	0.06
28	4	Anchorage-8	200.3313937	0	0	6	0	0	0.096
29	4	August-0.5	25.39955239	0	0	0	9	0	0.14
30	4	August-2.5	766.6697864	0	0	0	2.25	0	0.04
31	4	August-5	485.7871007	0	0	0	3.75	0	0.06
32	4	August-8	200.3313937	0	0	0	6	0	0.096
33	4	Marcopolo-0.5	25.39955239	0	0	0	0	9	0.14
34	4	Marcopolo-2.5	766.6697864	0	0	0	0	2.25	0.04
35	4	Marcopolo-5	485.7871007	0	0	0	0	3.75	0.06
36	4	Marcopolo-8	200.3313937	0	0	0	0	6	0.096
37	4	Z-2	203.9216684	0	0	0	0	0	0.024
38	4	A-2	203.9216684	0	0	0	0	0	0.06
39	4	G-1.5	582.001119	0.104	0.104	0.299	0.299	0.299	0.025
40	4	G-2.5	402.5500509	0.135	0.135	0.403333333	0.403333333	0.403333333	0.04
41	4	G-4	305.1449135	0.2585	0.2585	0.723333333	0.723333333	0.723333333	0.12
42	4	G-1.5	582.001119	0.104	0.104	0.299	0.299	0.299	0.025
43	4	G-2.5	402.5500509	0.135	0.135	0.403333333	0.403333333	0.403333333	0.04
44	4	G-4	305.1449135	0.2585	0.2585	0.723333333	0.723333333	0.723333333	0.12
45	4	H-0.5	13.18982706	0.555	0.555	1.616666667	1.616666667	1.616666667	0
46	4	H-1	608.5109359	0.33	0.33	0.97	0.97	0.97	0
47	4	H-2	394.3497965	0.4765	0.4765	1.423333333	1.423333333	1.423333333	0
48	4	H-4	151.9433367	0.665	0.665	1.906666667	1.906666667	1.906666667	0
49	4	H-0.5	13.18982706	0.555	0.555	1.616666667	1.616666667	1.616666667	0
50	4	H-1	608.5109359	0.33	0.33	0.97	0.97	0.97	0
51	4	H-2	394.3497965	0.4765	0.4765	1.423333333	1.423333333	1.423333333	0
52	4	H-4	151.9433367	0.665	0.665	1.906666667	1.906666667	1.906666667	0
53	4	Q-0.5	35.35220753	0	0	0	0	0	0.34
54	4	Q-1	204.8414852	0	0	0	0	0	0.04
55	4	Q-2	104.3558291	0	0	0	0	0	0.08
56	4	Q-4	51.26677518	0	0	0	0	0	0.16
57	4	Q-0.5	35.35220753	0	0	0	0	0	0.34
58	4	Q-1	204.8414852	0	0	0	0	0	0.04
59	4	Q-2	104.3558291	0	0	0	0	0	0.08
60	4	Q-4	51.26677518	0	0	0	0	0	0.16
61	4	Q-0.5	35.35220753	0	0	0	0	0	0.34
62	4	Q-1	204.8414852	0	0	0	0	0	0.04
63	4	Q-2	104.3558291	0	0	0	0	0	0.08
64	4	Q-4	51.26677518	0	0	0	0	0	0.16
65	4	Q-0.5	35.35220753	0	0	0	0	0	0.34
66	4	Q-1	204.8414852	0	0	0	0	0	0.04
67	4	Q-2	104.3558291	0	0	0	0	0	0.08
68	4	Q-4	51.26677518	0	0	0	0	0	0.16
69	4	Q-0.5	35.35220753	0	0	0	0	0	0.34
70	4	Q-1	204.8414852	0	0	0	0	0	0.04
71	4	Q-2	104.3558291	0	0	0	0	0	0.08
72	4	Q-4	51.26677518	0	0	0	0	0	0.16
73	4	T-3	261.8007121	0	0	0	0	0	0.045
74	4	T-4	182.1410987	0	0	0	0	0	0.06
75	4	T-6	107.3408952	0	0	0	0	0	0.09
76	2	B-4	63.85544525	0	0	0	0	0	0
77	2	B-4	63.85544525	0	0	0	0	0	0
78	2	B-4	63.85544525	0	0	0	0	0	0
79	2	B-4	63.85544525	0	0	0	0	0	0
80	2	B-4	63.85544525	0	0	0	0	0	0
81	2	B-4	63.85544525	0	0	0	0	0	0
82	2	B-4	63.85544525	0	0	0	0	0	0
83	2	B-4	63.85544525	0	0	0	0	0	0
84	2	B-4	63.85544525	0	0	0	0	0	0
85	2	B-4	31.92772262	0	0	0	0	0	0
86	2	B-4	31.92772262	0	0	0	0	0	0
87	2	C-6	331.5425296	0	0	0	0	0	0
88	2	C-8	224.3791833	0	0	0	0	0	0
89	2	C-12	170.3707535	0	0	0	0	0	0
90	2	C-6	331.5425296	0	0	0	0	0	0
91	2	C-8	224.3791833	0	0	0	0	0	0
92	2	C-12	170.3707535	0	0	0	0	0	0
93	2	Z-2	222.8618262	0	0	0	0	0	0
94	2	A-2	222.8618262	0	0	0	0	0	0
95	2	G-1.5	636.0571355	0	0	0	0	0	0
96	2	G-2.5	439.9387285	0	0	0	0	0	0
97	2	G-4	333.4866434	0	0	0	0	0	0
98	2	G-1.5	636.0571355	0	0	0	0	0	0
99	2	G-2.5	439.9387285	0	0	0	0	0	0
100	2	G-4	333.4866434	0	0	0	0	0	0
101	2	H-0.5	14.41489259	0	0	0	0	0	0
102	2	H-1	665.0291729	0	0	0	0	0	0
103	2	H-2	430.976838	0	0	0	0	0	0
104	2	H-4	166.0557692	0	0	0	0	0	0
105	2	H-0.5	14.41489259	0	0	0	0	0	0
106	2	H-1	665.0291729	0	0	0	0	0	0
107	2	H-2	430.976838	0	0	0	0	0	0
108	2	H-4	166.0557692	0	0	0	0	0	0
109	2	Q-0.5	38.63570553	0	0	0	0	0	0
110	2	Q-1	223.8670753	0	0	0	0	0	0
111	2	Q-2	114.0483541	0	0	0	0	0	0
112	2	Q-4	56.02841146	0	0	0	0	0	0
113	2	Q-0.5	38.63570553	0	0	0	0	0	0
114	2	Q-1	223.8670753	0	0	0	0	0	0
115	2	Q-2	114.0483541	0	0	0	0	0	0
116	2	Q-4	56.02841146	0	0	0	0	0	0
117	2	Q-0.5	38.63570553	0	0	0	0	0	0
118	2	Q-1	223.8670753	0	0	0	0	0	0
119	2	Q-2	114.0483541	0	0	0	0	0	0
120	2	Q-4	56.02841146	0	0	0	0	0	0
121	2	Q-0.5	38.63570553	0	0	0	0	0	0
122	2	Q-1	223.8670753	0	0	0	0	0	0
123	2	Q-2	114.0483541	0	0	0	0	0	0
124	2	Q-4	56.02841146	0	0	0	0	0	0
125	2	Q-0.5	38.63570553	0	0	0	0	0	0
126	2	Q-1	223.8670753	0	0	0	0	0	0
127	2	Q-2	114.0483541	0	0	0	0	0	0
128	2	Q-4	56.02841146	0	0	0	0	0	0
129	2	T-3	286.1166509	0	0	0	0	0	0
130	2	T-4	199.0582865	0	0	0	0	0	0
131	2	T-6	117.3106719	0	0	0	0	0	0
132	3	B-4	63.20796608	0	0	0	0	0	0
133	3	B-4	63.20796608	0	0	0	0	0	0
134	3	B-4	63.20796608	0	0	0	0	0	0
135	3	B-4	63.20796608	0	0	0	0	0	0
136	3	B-4	63.20796608	0	0	0	0	0	0
137	3	B-4	63.20796608	0	0	0	0	0	0
138	3	B-4	63.20796608	0	0	0	0	0	0
139	3	B-4	63.20796608	0	0	0	0	0	0
140	3	B-4	63.20796608	0	0	0	0	0	0
141	3	B-4	31.60398304	0	0	0	0	0	0
142	3	B-4	31.60398304	0	0	0	0	0	0
143	3	C-6	328.1807665	0	0	0	0	0	0
144	3	C-8	222.1040313	0	0	0	0	0	0
145	3	C-12	168.6432343	0	0	0	0	0	0
146	3	C-6	328.1807665	0	0	0	0	0	0
147	3	C-8	222.1040313	0	0	0	0	0	0
148	3	C-12	168.6432343	0	0	0	0	0	0
149	3	Z-2	220.6020598	0	0	0	0	0	0
150	3	A-2	220.6020598	0	0	0	0	0	0
151	3	G-1.5	629.6076661	0	0	0	0	0	0
152	3	G-2.5	435.4778534	0	0	0	0	0	0
153	3	G-4	330.1051674	0	0	0	0	0	0
154	3	G-1.5	629.6076661	0	0	0	0	0	0
155	3	G-2.5	435.4778534	0	0	0	0	0	0
156	3	G-4	330.1051674	0	0	0	0	0	0
157	3	H-0.5	14.26872898	0	0	0	0	0	0
158	3	H-1	658.2859339	0	0	0	0	0	0
159	3	H-2	426.6068344	0	0	0	0	0	0
160	3	H-4	164.3720029	0	0	0	0	0	0
161	3	H-0.5	14.26872898	0	0	0	0	0	0
162	3	H-1	658.2859339	0	0	0	0	0	0
163	3	H-2	426.6068344	0	0	0	0	0	0
164	3	H-4	164.3720029	0	0	0	0	0	0
165	3	Q-0.5	38.24394859	0	0	0	0	0	0
166	3	Q-1	221.5971159	0	0	0	0	0	0
167	3	Q-2	112.8919307	0	0	0	0	0	0
168	3	Q-4	55.46029657	0	0	0	0	0	0
169	3	Q-0.5	38.24394859	0	0	0	0	0	0
170	3	Q-1	221.5971159	0	0	0	0	0	0
171	3	Q-2	112.8919307	0	0	0	0	0	0
172	3	Q-4	55.46029657	0	0	0	0	0	0
173	3	Q-0.5	38.24394859	0	0	0	0	0	0
174	3	Q-1	221.5971159	0	0	0	0	0	0
175	3	Q-2	112.8919307	0	0	0	0	0	0
176	3	Q-4	55.46029657	0	0	0	0	0	0
177	3	Q-0.5	38.24394859	0	0	0	0	0	0
178	3	Q-1	221.5971159	0	0	0	0	0	0
179	3	Q-2	112.8919307	0	0	0	0	0	0
180	3	Q-4	55.46029657	0	0	0	0	0	0
181	3	Q-0.5	38.24394859	0	0	0	0	0	0
182	3	Q-1	221.5971159	0	0	0	0	0	0
183	3	Q-2	112.8919307	0	0	0	0	0	0
184	3	Q-4	55.46029657	0	0	0	0	0	0
185	3	T-3	283.2154955	0	0	0	0	0	0
186	3	T-4	197.0398824	0	0	0	0	0	0
187	3	T-6	116.1211694	0	0	0	0	0	0
"""
PROJECT_TABLE_S4 = """
0	4	B-4	185.4920312	0	0	0.346666667	0.346666667	0.346666667	0.0588
1	4	B-4	185.4920312	0	0	0.346666667	0.346666667	0.346666667	0.0588
2	4	B-4	185.4920312	0	0	0.346666667	0.346666667	0.346666667	0.0588
3	4	B-4	185.4920312	0	0	0.346666667	0.346666667	0.346666667	0.0588
4	4	B-4	185.4920312	0	0	0.346666667	0.346666667	0.346666667	0.0588
5	4	B-4	185.4920312	0	0	0.346666667	0.346666667	0.346666667	0.0588
6	4	B-4	185.4920312	0	0	0.346666667	0.346666667	0.346666667	0.0588
7	4	B-4	185.4920312	0	0	0.346666667	0.346666667	0.346666667	0.0588
8	4	B-4	185.4920312	0	0	0.346666667	0.346666667	0.346666667	0.0588
9	4	B-4	92.7460156	0	0	0.346666667	0.346666667	0.346666667	0.0588
10	4	B-4	92.7460156	0	0	0.346666667	0.346666667	0.346666667	0.0588
11	4	C-6	963.0893184	0	0	0	0	0	0.06
12	4	C-8	651.7932859	0.0645	0.0645	0.151	0.151	0.151	0.08
13	4	C-12	494.9055951	0.079	0.079	0.245333333	0.245333333	0.245333333	0.12
14	4	C-6	963.0893184	0	0	0	0	0	0.06
15	4	C-8	651.7932859	0.0645	0.0645	0.151	0.151	0.151	0.08
16	4	C-12	494.9055951	0.079	0.079	0.245333333	0.245333333	0.245333333	0.12
17	4	Agir-0.5	25.39955239	6	0	0	0	0	0.14
18	4	Agir-2.5	766.6697864	1.2	0	0	0	0	0.04
19	4	Agir-5	485.7871007	2.5	0	0	0	0	0.06
20	4	Agir-8	200.3313937	4	0	0	0	0	0.096
21	4	Hakuryu-0.5	25.39955239	0	6	0	0	0	0.14
22	4	Hakuryu-2.5	766.6697864	0	1.2	0	0	0	0.04
23	4	Hakuryu-5	485.7871007	0	2.5	0	0	0	0.06
24	4	Hakuryu-8	200.3313937	0	4	0	0	0	0.096
25	4	Anchorage-0.5	25.39955239	0	0	9	0	0	0.14
26	4	Anchorage-2.5	766.6697864	0	0	2.25	0	0	0.04
27	4	Anchorage-5	485.7871007	0	0	3.75	0	0	0.06
28	4	Anchorage-8	200.3313937	0	0	6	0	0	0.096
29	4	August-0.5	25.39955239	0	0	0	9	0	0.14
30	4	August-2.5	766.6697864	0	0	0	2.25	0	0.04
31	4	August-5	485.7871007	0	0	0	3.75	0	0.06
32	4	August-8	200.3313937	0	0	0	6	0	0.096
33	4	Marcopolo-0.5	25.39955239	0	0	0	0	9	0.14
34	4	Marcopolo-2.5	766.6697864	0	0	0	0	2.25	0.04
35	4	Marcopolo-5	485.7871007	0	0	0	0	3.75	0.06
36	4	Marcopolo-8	200.3313937	0	0	0	0	6	0.096
37	4	Z-2	647.3855544	0	0	0	0	0	0.024
38	4	A-2	647.3855544	0	0	0	0	0	0.06
39	4	G-1.5	1847.665921	0.104	0.104	0.299	0.299	0.299	0.025
40	4	G-2.5	1277.966633	0.135	0.135	0.403333333	0.403333333	0.403333333	0.04
41	4	G-4	968.7367243	0.2585	0.2585	0.723333333	0.723333333	0.723333333	0.12
42	4	G-1.5	1847.665921	0.104	0.104	0.299	0.299	0.299	0.025
43	4	G-2.5	1277.966633	0.135	0.135	0.403333333	0.403333333	0.403333333	0.04
44	4	G-4	968.7367243	0.2585	0.2585	0.723333333	0.723333333	0.723333333	0.12
45	4	H-0.5	41.87344863	0.555	0.555	1.616666667	1.616666667	1.616666667	0
46	4	H-1	1931.826043	0.33	0.33	0.97	0.97	0.97	0
47	4	H-2	1251.933469	0.4765	0.4765	1.423333333	1.423333333	1.423333333	0
48	4	H-4	482.3711089	0.665	0.665	1.906666667	1.906666667	1.906666667	0
49	4	H-0.5	41.87344863	0.555	0.555	1.616666667	1.616666667	1.616666667	0
50	4	H-1	1931.826043	0.33	0.33	0.97	0.97	0.97	0
51	4	H-2	1251.933469	0.4765	0.4765	1.423333333	1.423333333	1.423333333	0
52	4	H-4	482.3711089	0.665	0.665	1.906666667	1.906666667	1.906666667	0
53	4	Q-0.5	112.2318616	0	0	0	0	0	0.34
54	4	Q-1	650.3056765	0	0	0	0	0	0.04
55	4	Q-2	331.2961139	0	0	0	0	0	0.08
56	4	Q-4	162.7554832	0	0	0	0	0	0.16
57	4	Q-0.5	112.2318616	0	0	0	0	0	0.34
58	4	Q-1	650.3056765	0	0	0	0	0	0.04
59	4	Q-2	331.2961139	0	0	0	0	0	0.08
60	4	Q-4	162.7554832	0	0	0	0	0	0.16
61	4	Q-0.5	112.2318616	0	0	0	0	0	0.34
62	4	Q-1	650.3056765	0	0	0	0	0	0.04
63	4	Q-2	331.2961139	0	0	0	0	0	0.08
64	4	Q-4	162.7554832	0	0	0	0	0	0.16
65	4	Q-0.5	112.2318616	0	0	0	0	0	0.34
66	4	Q-1	650.3056765	0	0	0	0	0	0.04
67	4	Q-2	331.2961139	0	0	0	0	0	0.08
68	4	Q-4	162.7554832	0	0	0	0	0	0.16
69	4	Q-0.5	112.2318616	0	0	0	0	0	0.34
70	4	Q-1	650.3056765	0	0	0	0	0	0.04
71	4	Q-2	331.2961139	0	0	0	0	0	0.08
72	4	Q-4	162.7554832	0	0	0	0	0	0.16
73	4	T-3	831.1328586	0	0	0	0	0	0.045
74	4	T-4	578.2392675	0	0	0	0	0	0.06
75	4	T-6	340.7727365	0	0	0	0	0	0.09
"""

"""
Code copied from Alas (https://github.com/LmeSzinc/AzurLaneAutoScript)
Included so this utility can run as a standalone file
"""


class cached_property:
    """
    cached-property from https://github.com/pydanny/cached-property

    A property that is only computed once per instance and then replaces itself
    with an ordinary attribute. Deleting the attribute resets the property.
    Source: https://github.com/bottlepy/bottle/commit/fa7733e075da0d790d809aa3d2f53071897e6f76
    """

    def __init__(self, func):
        self.func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self

        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def timer(function):
    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()

        result = function(*args, **kwargs)
        t1 = time.time()
        print('%s: %s s' % (function.__name__, str(round(t1 - t0, 10))))
        return result

    return function_timer


class Filter:
    def __init__(self, regex, attr, preset=()):
        """
        Args:
            regex: Regular expression.
            attr: Attribute name.
            preset: Build-in string preset.
        """
        if isinstance(regex, str):
            regex = re.compile(regex)
        self.regex = regex
        self.attr = attr
        self.preset = tuple(list(p.lower() for p in preset))
        self.filter_raw = []
        self.filter = []

    def load(self, string):
        string = str(string)
        self.filter_raw = [f.strip(' \t\r\n') for f in string.split('>')]
        self.filter = [self.parse_filter(f) for f in self.filter_raw]

    def is_preset(self, filter):
        return len(filter) and filter.lower() in self.preset

    def apply(self, objs, func=None):
        """
        Args:
            objs (list): List of objects and strings
            func (callable): A function to filter object.
                Function should receive an object as arguments, and return a bool.
                True means add it to output.

        Returns:
            list: A list of objects and preset strings, such as [object, object, object, 'reset']
        """
        out = []
        for raw, filter in zip(self.filter_raw, self.filter):
            if self.is_preset(raw):
                raw = raw.lower()
                if raw not in out:
                    out.append(raw)
            else:
                for index, obj in enumerate(objs):
                    if self.apply_filter_to_obj(obj=obj, filter=filter) and obj not in out:
                        out.append(obj)

        if func is not None:
            objs, out = out, []
            for obj in objs:
                if isinstance(obj, str):
                    out.append(obj)
                elif func(obj):
                    out.append(obj)
                else:
                    # Drop this object
                    pass

        return out

    def apply_filter_to_obj(self, obj, filter):
        """
        Args:
            obj (object):
            filter (list[str]):

        Returns:
            bool: If an object satisfy a filter.
        """
        for attr, value in zip(self.attr, filter):
            if not value:
                continue
            if str(obj.__getattribute__(attr)).lower() != str(value):
                return False

        return True

    def parse_filter(self, string):
        """
        Args:
            string (str):

        Returns:
            list[strNone]:
        """
        string = string.replace(' ', '').lower()
        result = re.search(self.regex, string)

        if self.is_preset(string):
            return [string]

        if result and len(string) and result.span()[1]:
            return [result.group(index + 1) for index, attr in enumerate(self.attr)]
        else:
            print(f'Invalid filter: "{string}". This selector does not match the regex, nor a preset.')
            # Invalid filter will be ignored.
            # Return strange things and make it impossible to match
            return ['1nVa1d'] + [None] * (len(self.attr) - 1)


class SelectedGrids:
    def __init__(self, grids):
        self.grids = grids

    def __iter__(self):
        return iter(self.grids)

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.grids[item]
        else:
            return SelectedGrids(self.grids[item])

    def __contains__(self, item):
        return item in self.grids

    def __str__(self):
        # return str([str(grid) for grid in self])
        return '[' + ', '.join([str(grid) for grid in self]) + ']'

    def __len__(self):
        return len(self.grids)

    def __bool__(self):
        return self.count > 0

    # def __getattr__(self, item):
    #     return [grid.__getattribute__(item) for grid in self.grids]

    @property
    def location(self):
        """
        Returns:
            list[tuple]:
        """
        return [grid.location for grid in self.grids]

    @property
    def cost(self):
        """
        Returns:
            list[int]:
        """
        return [grid.cost for grid in self.grids]

    @property
    def weight(self):
        """
        Returns:
            list[int]:
        """
        return [grid.weight for grid in self.grids]

    @property
    def count(self):
        """
        Returns:
            int:
        """
        return len(self.grids)

    def select(self, **kwargs):
        """
        Args:
            **kwargs: Attributes of Grid.

        Returns:
            SelectedGrids:
        """
        result = []
        for grid in self:
            flag = True
            for k, v in kwargs.items():
                grid_v = grid.__getattribute__(k)
                if type(grid_v) != type(v) or grid_v != v:
                    flag = False
            if flag:
                result.append(grid)

        return SelectedGrids(result)

    def filter(self, func):
        """
        Filter grids by a function.

        Args:
            func (callable): Function should receive an grid as argument, and return a bool.

        Returns:
            SelectedGrids:
        """
        return SelectedGrids([grid for grid in self if func(grid)])

    def set(self, **kwargs):
        """
        Set attribute to each grid.

        Args:
            **kwargs:
        """
        for grid in self:
            for key, value in kwargs.items():
                grid.__setattr__(key, value)

    def get(self, attr):
        """
        Get an attribute from each grid.

        Args:
            attr: Attribute name.

        Returns:
            list:
        """
        return [grid.__getattribute__(attr) for grid in self.grids]

    def call(self, func, **kwargs):
        """
        Call a function in reach grid, and get results.

        Args:
            func (str): Function name to call.
            **kwargs:

        Returns:
            list:
        """
        return [grid.__getattribute__(func)(**kwargs) for grid in self]

    def add(self, grids):
        """
        Args:
            grids(SelectedGrids):

        Returns:
            SelectedGrids:
        """
        return SelectedGrids(list(set(self.grids + grids.grids)))

    def add_by_eq(self, grids):
        """
        Another `add()` method, but de-duplicates with `__eq__` instead of `__hash__`.

        Args:
            grids(SelectedGrids):

        Returns:
            SelectedGrids:
        """
        new = []
        for grid in self.grids + grids.grids:
            if grid not in new:
                new.append(grid)

        return SelectedGrids(new)

    def intersect(self, grids):
        """
        Args:
            grids(SelectedGrids):

        Returns:
            SelectedGrids:
        """
        return SelectedGrids(list(set(self.grids).intersection(set(grids.grids))))

    def intersect_by_eq(self, grids):
        """
        Another `intersect()` method, but de-duplicates with `__eq__` instead of `__hash__`.

        Args:
            grids(SelectedGrids):

        Returns:
            SelectedGrids:
        """
        new = []
        for grid in self.grids:
            if grid in grids.grids:
                new.append(grid)

        return SelectedGrids(new)

    def delete(self, grids):
        """
        Args:
            grids(SelectedGrids):

        Returns:
            SelectedGrids:
        """
        g = [grid for grid in self.grids if grid not in grids]
        return SelectedGrids(g)


def hr0(title):
    middle = '|' + ' ' * 20 + title + ' ' * 20 + '|'
    border = '+' + '-' * (len(middle) - 2) + '+'
    print(border)
    print(middle)
    print(border)


def hr1(title):
    print('=' * 20 + ' ' + title + ' ' + '=' * 20)


def hr2(title):
    print('-' * 20 + ' ' + title + ' ' + '-' * 20)


def hr3(title):
    print('<' * 3 + ' ' + title + ' ' + '>' * 3)


FILTER_REGEX = re.compile('([s\!][1234])?'
                          '-?'
                          '(neptune|monarch|ibuki|izumo|roon|saintlouis'
                          '|seattle|georgia|kitakaze|azuma|friedrich'
                          '|gascogne|champagne|cheshire|drake|mainz|odin'
                          '|anchorage|hakuryu|agir|august|marcopolo)?'
                          '(dr|pry)?'
                          '([bcdeghqtaz])?'
                          '-?'
                          '(\d.\d|\d\d?)?')
FILTER_ATTR = ('series', 'ship', 'ship_rarity', 'genre', 'duration')
FILTER_PRESET = ('shortest', 'cheapest', 'reset')
FILTER = Filter(FILTER_REGEX, FILTER_ATTR, FILTER_PRESET)

"""
Research optimizer start
"""


def parse_value(value):
    if '.' in value:
        try:
            return float(value)
        except ValueError:
            pass
    else:
        try:
            return int(value)
        except ValueError:
            pass
    return value


def parse_text_table(string, data_class):
    out = []
    for row in string.split('\n'):
        row = row.strip(' \r\n\t')
        if not len(row):
            continue
        row = row.split('\t')
        out.append(data_class(*row))
    return SelectedGrids(out)


@dataclass()
class Research:
    """
    Store information for each research project
    """
    index: int
    series: str
    name: str
    weight: float
    bp_Agir: float
    bp_Hakuryu: float
    bp_Anchorage: float
    bp_August: float
    bp_Marcopolo: float
    bp_Tenrai: float

    def __post_init__(self):
        # Convert value types
        for k, v in self.__dict__.items():
            self.__setattr__(k, parse_value(v))
        # Build object attributes required by the research filter
        self.genre, self.duration = self.name.split('-')
        self.duration = str(self.duration)
        if self.series == 4:
            self.series = f'S{self.series}'
        else:
            self.series = f'!4'
        if self.genre in ['Agir', 'Hakuryu']:
            self.ship = self.genre
            self.ship_rarity = 'dr'
            self.genre = 'D'
        elif self.genre in ['Anchorage', 'August', 'Marcopolo']:
            self.ship = self.genre
            self.ship_rarity = 'pry'
            self.genre = 'D'
        else:
            self.ship = ''
            self.ship_rarity = ''

    def __hash__(self):
        return hash(self.name)


PROJECTS = parse_text_table(PROJECT_TABLE, Research)
PROJECTS_S4 = parse_text_table(PROJECT_TABLE_S4, Research)


def product_dict(func):
    out = {}
    for project in PROJECTS:
        out[project.index] = func(project)
    return out


# Add a tiny reward floor so a malformed filter does not produce a non-terminating simulation
PROJECT_DROP = product_dict(lambda project: np.array(
    [project.bp_Agir, project.bp_Hakuryu, project.bp_Anchorage, project.bp_August, project.bp_Marcopolo,
     project.bp_Tenrai]) + 0.000001)
PROJECT_DURATION = product_dict(lambda project: float(project.duration) / 24)
# Build the drop-data array for numba
# Shape: (project_index=188, drop_items=6)
PROJECT_DROP_ARRAY = np.array(list(PROJECT_DROP.values()))
PROJECT_DURATION_ARRAY = np.array(list(PROJECT_DURATION.values()))


class ResearchPool:
    remove_projects = 'B > T > E'
    all_ships = ('Agir', 'Hakuryu', 'Anchorage', 'August', 'Marcopolo')

    def __init__(self, string):
        FILTER.load(string)
        self.filter = SelectedGrids(FILTER.apply(PROJECTS.grids))
        self.reset_index = 1000
        for index, project in enumerate(self.filter):
            if str(project) == 'reset':
                self.reset_index = index
                break

    @cached_property
    def project_select_index(self):
        """
        Convert a filter string to project-selection indices; lower is higher priority, and 1000 means skip and refresh

        Returns:
            np.ndarray: Shape (188,), lower index means to be selected first. 1000 for not selected projects.
        """
        out = np.ones((PROJECTS.count,), dtype=int) * 1000
        for index, project in enumerate(self.filter):
            if index != self.reset_index:
                out[project.index] = index

        FILTER.load(ResearchPool.remove_projects)
        projects = FILTER.apply(PROJECTS.grids)
        for project in projects:
            out[project.index] = 1000
        return out

    @classmethod
    def cal_project_spawn_rate(cls, projects):
        """
        Calculate appearance probabilities for different completion states

        Returns:
            dict(tuple, np.ndarray): Key: Combinations of conditions, such as b'\x00\x00\x00\x00\x00\x00'
                value: project appear rate.
        """
        out = {}
        for condition in itertools.product([False, True], repeat=len(PROJECT_DROP[0])):
            ships = [ship for ship, con in zip(cls.all_ships, condition) if con]
            weight = np.array(projects.get('weight'))
            index = np.sum(np.array(condition) * [1, 2, 4, 8, 16, 32])
            remain = len(ships)
            if 0 < remain < 5:
                changed = []
                # Transfer all Series 4 ship probability to unfinished ships
                for ship in ships:
                    for project in projects.select(ship=ship):
                        weight[project.index] *= 5 / remain
                        changed.append(project.index)
                # Set targeted probability for completed research ships to zero
                for project in projects.select(genre='D'):
                    if project.index not in changed:
                        weight[project.index] = 0
            weight /= np.sum(weight)
            out[index] = weight
        return out


SPAWN_RATE = ResearchPool('reset').cal_project_spawn_rate(PROJECTS)
SPAWN_RATE_S4 = ResearchPool('reset').cal_project_spawn_rate(PROJECTS_S4)
# Build refresh-probability arrays for different states for numba
# Precompute cumulative probability to speed up random_choice()
SPAWN_RATE = np.array([np.cumsum(SPAWN_RATE[n]) for n in range(64)])
SPAWN_RATE_S4 = np.array([np.cumsum(SPAWN_RATE_S4[n]) for n in range(64)])


@jit(nopython=True, fastmath=True)
def random_choice(size, possibility_cumsum):
    """
    A minimal implementation of numpy.random.choice()
    Required because numba does not support the p probability-array argument of numpy.random.choice()
    https://numba.pydata.org/numba-doc/dev/reference/numpysupported.html

    Args:
        size (int): Only one-dimensional arrays are supported
        possibility_cumsum (np.ndarray): Cumulative appearance probabilities
    """
    rdm_unif = np.random.rand(size)
    return np.searchsorted(possibility_cumsum, rdm_unif)


@jit(nopython=True, fastmath=True)
def sample(condition, project_select_index, reset_index):
    """
    Generate random research projects and choose one

    Args:
        condition (np.ndarray): Shape (6,), completion state for each reward category
        project_select_index (np.ndarray): Shape (188,), lower values have higher priority; 1000 means skip and refresh
        reset_index (int): Priority value assigned to refresh

    Returns:
        int, int: Selected project with refresh available, selected project without refresh
    """
    while 1:
        # Convert completion state to an array index
        index = 0
        for i, c in enumerate(condition):
            if c:
                index += 2 ** i
        # Generate five projects: three Series 4 and two unrestricted
        # np.random.seed(3)
        p1, p2, p3 = random_choice(3, SPAWN_RATE_S4[index])
        p4, p5 = random_choice(2, SPAWN_RATE[index])
        # Remove duplicates
        if p1 == p4 or p2 == p4 or p3 == p4 or p1 == p5 or p2 == p5 or p3 == p5:
            continue
        # Add refresh; 1000 represents refresh
        project_list = np.array([p1, p2, p3, p4, p5, 1000])
        # Convert project indices to filter indices
        f1, f2, f3, f4, f5 = np.take(project_select_index, project_list[:5])
        # print(filter_index)
        # print(project_list)

        # Project selected when refresh is unavailable
        s_index = np.array([f1, f2, f3, f4, f5, 999])
        selected_no_reset = project_list[np.argmin(s_index)]
        # Project selected when refresh is available
        s_index = np.array([f1, f2, f3, f4, f5, reset_index])
        selected_with_reset = project_list[np.argmin(s_index)]

        return selected_with_reset, selected_no_reset


@jit(nopython=True, fastmath=True)
def events_add(rewards, condition):
    # Give event-exchange blueprints to the slowest-progress ship to improve overall completion time
    # G-series rewards are random; assigning exchange BPs to the slowest ship reduces overflow
    index = np.argmin(rewards[:2])
    rewards[index] += 0.5  # 15 DR blueprints in each event
    index = np.argmin(rewards[2:5])
    rewards[index + 2] += 1  # 30 PRY blueprints in each event
    return rewards


@jit(nopython=True, fastmath=True)
def simulate(project_select_index, reset_index, target, active=1., interval=0.):
    """
    Simulate one player's research progression until completion

    Args:
        project_select_index (np.ndarray): Shape (188,), lower values have higher priority; 1000 means skip and refresh
        reset_index (int): Priority value assigned to refresh
        target (np.ndarray): Shape (6,), target reward quantities
        active (float): Daily active window in days; existing projects continue afterward but no new project starts
        interval (float): Collection delay in days after a project completes

    Returns:
        float, np.ndarray: Elapsed time and cumulative rewards, shape (6,)
    """
    rewards = np.array([0., 0., 0., 0., 0., 0.])
    condition = rewards != 0  # Whether each reward target is unfinished: True unfinished, False complete
    has_reset = True
    day_cost = 0

    while 1:
        """
        Run one research project
        """
        while 1:
            index, index_no_reset = sample(condition, project_select_index, reset_index)
            # print(index, index_no_reset, has_reset)
            if has_reset:
                if index == 1000:
                    has_reset = False
                    continue
                else:
                    break
            else:
                if index_no_reset == 1000:
                    # If refreshes are exhausted but one is required, wait for the next day's refresh
                    day_cost = int(day_cost) + 1
                    rewards = events_add(rewards, condition)
                    has_reset = False
                    continue
                else:
                    index = index_no_reset
                    break

        """
        Collect a research project and calculate rewards and elapsed time
        """
        prev_day = int(day_cost)
        rewards += PROJECT_DROP_ARRAY[index]
        day_cost += PROJECT_DURATION_ARRAY[index] + interval
        # print(rewards / day_cost)
        condition = rewards < target
        new_day = int(day_cost)
        new_hour = day_cost - new_day
        # Reset refresh count across the daily boundary
        if new_day > prev_day:
            has_reset = True
            rewards = events_add(rewards, condition)
        else:
            # Outside the active window
            if new_hour > active:
                day_cost = int(day_cost) + 1
                has_reset = True
                rewards = events_add(rewards, condition)

        """
        Reach all target reward quantities
        """
        if not np.any(condition):
            break

    return day_cost, rewards


class FilterSimulator:
    active = 24 / 24
    interval = 0 / 60 / 24
    target = np.array([513, 513, 343, 343, 343, 150])

    def __init__(self, string):
        string = string.replace('E-315', 'A2')
        string = string.replace('E-031', 'Z2')
        self.string = string
        self.pool = ResearchPool(string)

    def run(self, sample_count=1000):
        day_cost = 0
        rewards = PROJECT_DROP[0] * 0
        for _ in tqdm(range(sample_count)):
            sim_day, sim_rewards = simulate(
                self.pool.project_select_index,
                self.pool.reset_index,
                target=FilterSimulator.target,
                active=FilterSimulator.active,
                interval=FilterSimulator.interval
            )
            day_cost += sim_day
            rewards += sim_rewards
        day_cost /= sample_count
        rewards /= sample_count

        hr3('End Testing')
        print(self.string)
        print(f'Average time cost: {day_cost}')
        print(f'Average rewards: {rewards}')

        return day_cost


def split_filter(string):
    if isinstance(string, list):
        return string
    return [f.strip(' \t\r\n') for f in string.split('>')]


def join_filter(selection):
    if isinstance(selection, str):
        return selection
    return ' > '.join(selection)


def beautify_filter(list_filter):
    if isinstance(list_filter, str):
        list_filter = split_filter(list_filter)

    out = []
    length = 0
    for selection in list_filter:
        if length + len(selection) + 3 > 70:
            out.append('\n')
            length = 0
        out.append(selection)
        length += len(selection) + 3
    string = ' > '.join(out).strip('\n >').replace(' > \n', '\n').replace('\n ', '\n')
    return string


def position_change(string, position):
    selection = split_filter(string)
    selection[position], selection[position + 1] = selection[position + 1], selection[position]
    return join_filter(selection)


def position_insert(string, insert, position):
    selection = split_filter(string)
    selection.insert(position, insert)
    return join_filter(selection)


def epoch_worker(data):
    index, total, sample_count, select_index, forward_index, string = data
    hr3(f'Start Testing: {index}/{total}')
    return FilterSimulator(string).run(sample_count)


class BruteForceOptimizer:
    @timer
    def optimize(self, string, diff=10):
        for epoch in range(100):
            hr0(f'Epoch: {epoch}')
            new, diff = self.epoch(string, diff=diff)
            if new == string:
                break
            else:
                string = new
                continue

    def gen(self, string, look_forward):
        string = split_filter(string)
        yield 0, 0, join_filter(string)

        for select_index, select_item in enumerate(string):
            string_dropped = [s for s in string if s != select_item]
            for forward_index in range(1, look_forward + 1):
                forward_index = select_index - forward_index
                if forward_index < 0:
                    continue
                string_added = deepcopy(string_dropped)
                string_added.insert(forward_index, select_item)
                string_added = join_filter(string_added)
                yield select_index, select_index - forward_index, string_added

    def epoch(self, string, diff=10):
        diff = min(abs(diff), 1)
        level = np.log(diff) / np.log(10) + 1
        sample_count = int(np.power(10, 5 - level / 2))
        look_forward = int(np.power(3, level))
        look_forward = max(look_forward, 1)
        sample_count = min(max(sample_count, 10000), 300000)
        print(f'diff: {diff}, look_forward: {look_forward}, sample_count: {sample_count}')

        string_split = split_filter(string)
        string_count = len(string_split)
        all_tests = list(self.gen(string, look_forward=look_forward))
        total = len(all_tests)
        # index, total, sample_count, select_index, forward_index, string_added
        tests_data = [(index, total, sample_count, *row) for index, row in enumerate(all_tests)]

        results = process_map(epoch_worker, tests_data, max_workers=BruteForceOptimizer.process)

        day_cost = np.ones((string_count, look_forward + 1)) * 1000
        for data, result in zip(tests_data[1:], results[1:]):
            day_cost[data[3]][data[4]] = result
        day_cost[:, 0] = results[0]

        hr2('Original filter')
        print(beautify_filter(string_split))

        hr2('Move forward')
        forward = np.argmin(day_cost, axis=1)
        if look_forward == 1:
            forward[np.min(day_cost, axis=1) != np.min(day_cost)] = 0
        for index, selection, forward_index in zip(range(len(forward)), string_split, forward):
            if index == 0:
                selection = '[Original]'
            print(f'{selection.ljust(12, " ")}forward: {forward_index}, day_cost: {day_cost[index][forward_index]}')
        diff = day_cost[0][0] - np.min(day_cost)
        print(f'diff: {diff}')

        hr2('New filter')
        forward[forward > 0] += 1
        forward = np.arange(forward.shape[0]) - forward
        new_index = np.argsort(forward)
        new_filter = beautify_filter([string_split[index] for index in new_index])
        print(new_filter)

        return new_filter, diff


"""
Research settings
"""
# Excluded research projects
# Exclude B/T/E by default because their drop-data sample is small
# Spend cubes: 'B > T > E'
# Only run 0.5-hour cube projects: 'B > T > E > H1 > H2 > H4'
# Do not spend cubes: 'B > T > E > H'
ResearchPool.remove_projects = 'B > T > H1 > H2 > H4'
# Daily active time, measured in days
# Existing projects continue after the active window, but no new project starts
FilterSimulator.active = 24 / 24
# Collection interval, measured in days
# Delay between project completion and collection
FilterSimulator.interval = 0 / 60 / 24
# Research targets
# Required quantities: rainbow BPs, rainbow BPs, gold BPs, gold BPs, gold BPs, rainbow gear
# Stop targeted projects for a completed BP category; reset after all BP targets are complete
# Complete Series 4: np.array([513, 513, 343, 343, 343, 100])
# Research ships only: np.array([513, 513, 343, 343, 343, 0])
# Rainbow gear only: np.array([0, 0, 0, 0, 0, 150])
FilterSimulator.target = np.array([513, 513, 343, 343, 343, 100])
# Number of worker processes
# Recommended: number of physical CPU cores
BruteForceOptimizer.process = 6

if __name__ == '__main__':
    """
    This file contains both a simulator and an optimizer; uncomment the relevant section to run it
    Alas users need to install numba separately; no version is pinned
    Standalone use requires Python >= 3.7 and numba==0.45.1, llvmlite==0.29.0, numpy, and tqdm

    The filter is mostly compatible with the Alas research filter; see the repository filter documentation
    Additional constraints:
    - Exactly one reset entry is required
    - Alas presets cannot be used; for example, expand shortest into
      0.5 > 1 > 1.5 > 2 > 2.5 > 3 > 4 > 5 > 6 > 8 > 10 > 12
    - Recommended selection count: 10-24 entries
      Too few entries makes completion excessively slow
      Too many entries makes optimization excessively slow
    - The ! operator means NOT and may only be used on series numbers
      For example, !4 means not Series 4; see the FILTER_REGEX expression

    When running inside the Alas directory, uncomment this code to also write progress to the log
    """
    # from module.logger import logger
    # import builtins
    # builtins.print = logger.info
    """
    Simulate many users with one filter to estimate average completion time and final rewards
    Uncomment this section, paste the filter, and run it; an i7-8700K takes about 4.5 minutes
    """
    # simulator = FilterSimulator("""
    # S4-DR0.5 > S4-PRY0.5 > S4-Q0.5 > S4-H0.5 > Q0.5 > S4-DR2.5
    # > S4-G1.5 > S4-Q1 > S4-DR5 > 0.5 > S4-G4 > S4-Q2 > S4-PRY2.5 > reset
    # > S4-DR8 > Q1 > 1 > S4-E-315 > S4-G2.5 > G1.5 > 1.5 > S4-E-031
    # > S4-Q4 > Q2 > E2 > 2 > DR2.5 > PRY2.5 > G2.5 > 2.5 > S4-PRY5
    # > S4-PRY8 > Q4 > G4 > 4 > S4-C6 > DR5 > PRY5 > 5 > C6 > 6 > S4-C8
    # > S4-C12 > DR8 > PRY8 > C8 > 8 > C12 > 12
    # """)
    # simulator.run(sample_count=300000)
    """
    Optimize a filter by reordering selections to minimize completion time for the target
    The search resembles an early machine-learning optimizer: move distance shrinks and sample size grows as it converges
    Uncomment this section to run it; an i7-8700K takes approximately one to two days
    A roughly ordered filter containing all options is provided as the starting point
    """
    optimizer = BruteForceOptimizer()
    optimizer.optimize("""
    S4-H0.5 > S4-DR0.5 > S4-PRY0.5 > S4-Q0.5 > !4-0.5 > S4-G1.5 > S4-Q1 > S4-DR2.5
    > S4-G4 > S4-Q4 > S4-DR5 > S4-DR8 > S4-Q2 > S4-PRY2.5 > S4-G2.5 > !4-1
    > S4-H1 > S4-H2 > S4-H4
    > S4-EP2 > S4-EB2
    > reset > S4-PRY8 > !4-1.5 > S4-PRY5 > !4-2.5 > !4-2 > !4-4
    > S4-C6 > !4-C8 > S4-C8 > !4-C6 > S4-C12 > !4-C12
    """, diff=1)
