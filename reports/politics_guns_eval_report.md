# FileGraphDB Evaluation Report

Folder: `C:\Users\user\Downloads\twenty+newsgroups\20_newsgroups\20_newsgroups\talk.politics.guns`
Eval file: `samples\eval\politics_guns_eval.jsonl`
Limit: `10`
Input token price used: `$0.15` per 1M input tokens

## Summary

- Cases: 4
- Hit@K: 0.5000
- MRR: 0.3125
- Mean file recall: 0.3333
- Mean answer-term recall: 1.0000
- Mean token savings: 97.4100%

## Case 1

Query: `US UK handgun deaths statistics comparison`

Expected files:

- `53294`
- `53327`
- `53353`

Selected files:

- `53327`
- `53353`
- `53323`
- `53362`
- `53294`
- `53295`
- `53324`
- `53299`
- `53293`
- `53356`

Matched expected files:

- `53294`
- `53327`
- `53353`

Rank of first expected file: `1`
File recall: `1.0000`
Matched answer terms: `uk, us, handgun-related deaths, fbi statistics`
Answer-term recall: `1.0000`

Token and cost comparison:

- All-docs input tokens: `511502`
- FileGraphDB input tokens: `6359`
- Saved input tokens: `505143`
- Saved percent: `98.76%`
- All-docs estimated cost: `$0.0767253`
- FileGraphDB estimated cost: `$0.00095385`
- Estimated saved cost: `$0.07577145`

Evidence answer preview:

- `53327` score=0.529: Subject: Re: Gun Control (was Re: We're Mad as Hell at the TV News) J. Spencer (J.M.Spencer@newcastle.ac.uk) wrote: : manes@magpie.linknet.com (Steve Manes) writes: : >Jim De Arras (jmd@cube.handheld.com) wrote: : >: > Last year the US suffered almost 10,000 wrongful or accidental : >: > deaths by handguns alone (FBI statistics). In the same year, the UK : >: > suffered 35 such deaths (Scotland Yard statistics). The population : >: > of the UK is about 1/5 that of the US (10,000 / (35 * 5)). Weighted : >: > for population, the US has 57x as many handgun-related deaths as the : >: > UK. And, no, the Brits don't make up for this by murdering 57x as : >: > many people with baseball bats. : [snip] : If you examine the figures, they do. Stabbing is favourite, closely : followed by striking, punching, kicking. Many more people are burnt to : death in Britain as are shot to death. Take at look 
- `53353` score=0.507: Subject: Re: Gun Control (was Re: We're Mad as Hell at the TV News) In article <C518B1.AMF@magpie.linknet.com> manes@magpie.linknet.com (Steve Manes) writes: >: >: > Last year the US suffered almost 10,000 wrongful or accidental >: >: > deaths by handguns alone (FBI statistics). In the same year, the UK >: >: > suffered 35 such deaths (Scotland Yard statistics). The population >: >: > of the UK is about 1/5 that of the US (10,000 / (35 * 5)). Weighted >: >: > for population, the US has 57x as many handgun-related deaths as the >: >: > UK. And, no, the Brits don't make up for this by murdering 57x as >: >: > many people with baseball bats. >: If you examine the figures, they do. Stabbing is favourite, closely >: followed by striking, punching, kicking. Many more people are burnt to >: death in Britain as are shot to death. Take at look and you'll see for >: yourself. >It means that very f
- `53323` score=0.490: Subject: Re: Gun Control (was Re: We're Mad as Hell at the TV News) In article <C4u3x5.Fw7@magpie.linknet.com> manes@magpie.linknet.com (Steve Manes) writes: >I don't know how anyone can state that gun control could have NO >effect on homicide rates. I don't think anyone is arguing that there would be no effect. But there would be no _net_ _positive_ effect. You also have to consider the negative side: Law abiding citizens, armed with fireamrs (pistols for the most part), prevent between 80,000 (National Crime Survey) and 1,000,000 (Dr. Kleck) crimes each year. (Those are the extremes. Most studies find the number to be 500,000 to 600,000.) About 1% of those crimes are homicides, so private ownership of firearms _saves_ approximately 5,000 lives each year. There are roughly 12,000 criminal homicides and fatal accidents involving guns each year. For there to be any net benefit, you would 

## Case 2

Query: `Second Amendment right to keep and bear arms`

Expected files:

- `53302`
- `53332`
- `54163`

Selected files:

- `55486`
- `54571`
- `54687`
- `54163`
- `54689`
- `55232`
- `54707`
- `54218`
- `54453`
- `55048`

Matched expected files:

- `54163`

Rank of first expected file: `4`
File recall: `0.3333`
Matched answer terms: `second amendment, keep and bear, right`
Answer-term recall: `1.0000`

Token and cost comparison:

- All-docs input tokens: `511502`
- FileGraphDB input tokens: `9556`
- Saved input tokens: `501946`
- Saved percent: `98.13%`
- All-docs estimated cost: `$0.0767253`
- FileGraphDB estimated cost: `$0.0014334`
- Estimated saved cost: `$0.0752919`

Evidence answer preview:

- `55486` score=0.634: Subject: Re: Rewording the Second Amendment (ideas) A well-regulated militia, being necessary to the security of the FREE State, the right of the people to KEEP and BEAR arms, shall not be infringed. I know that as a Canadian, I don't have much to stand on... But, I think that the right to KEEP and BEAR arms is very important to maintaining a FREE society. The America is still the most enviable place to live on this Earth (by anyone with their head on straight) and will stay that way only if more people stand-up PUBLICLY for what they believe!! Remember, that if you stand for nothing... You'll fall for anything... including "well-meaning" socialists, they did in Canada. later TED
- `54571` score=0.535: Subject: Re: Some more about gun control... In article <C5L0n2.5LL@ulowell.ulowell.edu>, jrutledg@cs.ulowell.edu (John Lawrence Rutledge) writes: > >So the phrase "the right of the people to keep and bear Arms, shall >not be infringed" must either qualify or explain the phrase "a well >regulated militia, being necessary to the security of a free state." [stuff deleted] >Since "the right of the people to keep and bear Arms, shall not be >infringed" does not describe, modify or make less harsh anything and >it has nothing to do with grammar or some sort of position or task. >By process of elimination it must fall into definition #3. And since >#3 deals with legal power, the same thing the Constitution does, it >must be the correct definition in this case. Therefore, "the right >of the people to keep and bear Arms" gives legal power to the "well >regualated militia" and this legal power "sh
- `54687` score=0.526: Subject: Analysis of Second Amendment (Was: Re: Some more about gun control...) In article <1993Apr21.042608.26086@ra.msstate.edu> dnewcomb@whale.st.usm.edu (Donald R. Newcomb) writes: >First, I would like to say how much I appreciate having so literate and >erudite an individual as Mr. Rutledge with whom to discuss this topic. >Frankly, most anti-RKBA posters refuse even to approach the topic of >the original understanding of the Bill of Rights as detailed in the >writings of the era. This is most refreshing. > >Second, I must apologize for leaving the discussion for several days. >My brigade's quarterly drill was this weekend and I needed to attend >to several matters pertaining to the State Militia. > >Some people seem to feel that the concept of the Militia is an anachro- >nism that is out of place in the 20th century. I'm not sure the Swiss >would agree and I think perhaps a discuss

## Case 3

Query: `Brady Bill waiting period background check`

Expected files:

- `53296`
- `53308`
- `53323`

Selected files:

- `54454`
- `54258`
- `54199`
- `54708`
- `55426`
- `55488`
- `54233`
- `54314`
- `54684`
- `53310`

Matched expected files:

- `(none)`

Rank of first expected file: `None`
File recall: `0.0000`
Matched answer terms: `brady bill, waiting period, background check`
Answer-term recall: `1.0000`

Token and cost comparison:

- All-docs input tokens: `511502`
- FileGraphDB input tokens: `22705`
- Saved input tokens: `488797`
- Saved percent: `95.56%`
- All-docs estimated cost: `$0.0767253`
- FileGraphDB estimated cost: `$0.00340575`
- Estimated saved cost: `$0.07331955`

Evidence answer preview:

- `54454` score=0.590: Subject: Re: Handgun Restrictions >To: bbs.billand@tsoft.net >Subject: Re: Handgun Restrictions >Newsgroups: talk.politics.guns >In-Reply-To: <ow522B2w165w@tsoft.net> >Organization: Cray Research, Inc. >Cc: >Bcc: > In article <ow522B2w165w@tsoft.net> you write: >I would like to know what restrictions there are on purchasing handguns >(ie waiting periods, background check etc..) in the states of Nevada and >Oregon. Thanks. > -Bill > >-- >Bill Anderson (bbs.billand@tsoft.net) In Oregon your must get a background check (ie fingerprints, full slap), 15 day waiting period. That is unless you have a CCW then all requirments have been meet. Ernie Smith ernie@oregon.cray.com
- `54258` score=0.580: Subject: Handgun Restrictions I would like to know what restrictions there are on purchasing handguns (ie waiting periods, background check etc..) in the states of Nevada and Oregon. Thanks. -Bill -- Bill Anderson (bbs.billand@tsoft.net)
- `54199` score=0.529: Subject: S414 (Brady bill) loopholes? Hi. I've just finished reading S414, and have several questions about the Brady bills (S414 and HR1025). 1. _Are_ these the current versions of the Brady bill? What is the status of these bills? I've heard they're "in committee". How close is that to being made law? 2. S414 and HR1025 seem fairly similar. Are there any important differences I missed? 3. S414 seems to have some serious loopholes: A. S414 doesn't specify an "appeals" process to wrongful denial during the waiting period, other than a civil lawsuit(?) (S414 has an appeals process once the required instant background check system is established, but not before). B. the police are explicitly NOT liable for mistakes in denying/approving using existing records (so who would I sue in "A" above to have an inaccurate record corrected?) C. S414 includes an exception-to-waiting-period clause for 

## Case 4

Query: `Waco Branch Davidian raid compound attacked`

Expected files:

- `53297`
- `53315`
- `53361`

Selected files:

- `54508`
- `54843`
- `54306`
- `54699`
- `54400`
- `55053`
- `54407`
- `54509`
- `54284`
- `55067`

Matched expected files:

- `(none)`

Rank of first expected file: `None`
File recall: `0.0000`
Matched answer terms: `waco, branch davidians, compound`
Answer-term recall: `1.0000`

Token and cost comparison:

- All-docs input tokens: `511502`
- FileGraphDB input tokens: `14354`
- Saved input tokens: `497148`
- Saved percent: `97.19%`
- All-docs estimated cost: `$0.0767253`
- FileGraphDB estimated cost: `$0.0021531`
- Estimated saved cost: `$0.0745722`

Evidence answer preview:

- `54508` score=0.421: Subject: WACO: Clinton press conference, part 1 Here is a press release from the White House. President Clinton's Remarks On Waco With Q/A To: National Desk Contact: White House Office of the Press Secretary, 202-456-2100 WASHINGTON, April 20 -- Following are remarks by President Clinton in a question and answer session with the press: 1:36 P.M. EDT THE PRESIDENT: On February the 28th, four federal agents were killed in the line of duty trying to enforce the law against the Branch Davidian compound, which had illegally stockpiled weaponry and ammunition, and placed innocent children at risk. Because the BATF operation had failed to meet its objective, a 51-day standoff ensued. The Federal Bureau of Investigation then made every reasonable effort to bring this perilous situation to an end without bloodshed and further loss of life. The Bureau's efforts were ultimately unavailing because t
- `54843` score=0.391: Subject: Waco headlines and editorial in Boston Globe Boston Globe, Wednesday April 21 1993 col. 4 "Bodies found in ruins as FBI defends raid on cult ranch" col. 5 "Clinton blames Koresh, orders probe of siege" col. 2 "The children: panws in a horrifying game" pg. 18, col. 1, Editorial page "Judgment at Waco" Now the scientific and political scrutiny of the horror show in Waco begins, though nothing can undo the tragedy that might have been prevented there. Forensic experts will study the rubble and ashes of the Branch Davidian compound, where at least 85 people, including 24 children, perished in smoke and fire caused by theapocalyptic visions of a manipulative madman AND A STUNNING LAPSE IN JUDGMENT BY FEDERAL LAW ENFORCEMENT OFFICIALS. [emphasis added by me] Investigators will re-create conditions at the compound and identify accelerants and other fac- tors fueling the inferno. That i
- `54306` score=0.391: Subject: Re: Ax the ATF A few comments on the ATF's botched handling of this case: 1. Attempting to storm the compound in broad daylight? The explanation we were given (at least at one point) was that they thought the cult members would be at religious services. My only comment on this bit of idiocy is that if you're going to operate as a quasi-military unit, you'd better understand basic military tactics. One cardinal rule is that only a fool plans an operation where if one assumption is incorrect, the operation will fail disastrously. 2. We were told that ATF got four agents killed because they were outgunned, they didn't expect such heavy resistance. When questioned about why such an overwhelming military-style assault was planned, we were told that it was because the cultists were thought to be heavily armed. Can you say contradictory? I knew you could! 3. The BATF has had a bad repu
