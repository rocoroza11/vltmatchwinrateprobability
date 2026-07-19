**\*\* ROUND1 \& ROUND2 / ROUND 13 \& ROUND 14 \*\***

**dataset: 15/16 round 2 conv.; 12/14 round 14 conv.**



// NO SIDE CONDITIONING.

**(1,1) prior w original dataset**

mean: \[0.88888889 0.8125]

ci\_lower: \[0.7131106 0.5953973]

ci\_upper: \[0.98542068 0.95668799]

ci\_width: \[0.27231008 0.36129069]



* With heavy uncertainty due to small sample size, the probability that the very next pistol round (round 1) that Fnatic play through will have an 88.8% chance of conversion into round 2; and round 13 has a 81.3% chance of conversion into round 14. 
* Results show that Fnatic will convert a pistol round -> round 2 with a 71.3% chance in <5% occurrences and 98.5% in >95% occurrences. This is expected as Fnatic are a professional team, who finished 5-0 in Stage 1.
* However, the probability that they convert a round 13 victory -> round 14 is 59.5% in <5% occurrences, and 95.6% in >95% occurrences. This seems anomalous, on both sides of the confidence interval. A 59.5% shows a struggle to build up momentum, perhaps due to the half time break and the physical/mental rest? Whilst a 95.6% implies the contrary; that they build and keep up momentum. It is important to note that a roster change did occur during this time, with Veqaj being inactive and his position being filled-in by several members (Desmo, CyvOph). 
* The CI is very very wide for each round scenario. I think more samples would resolve this. 



// NO SIDE CONDITIONING.

**adjusted priors (9,1) w n0 = 10.**

mean: \[0.92307692 0.875]

ci\_lower: \[0.79648309 0.71962066]

ci\_upper: \[0.99016041 0.97224849]

ci\_width: \[0.19367732 0.25262783]



* With lesser uncertainty due to introduction of hypothetical pseudo-rounds, the probability that the very next pistol round (round 1) that Fnatic will play through has a 92.3% chance of conversion into round 2; and round 13 has an 87.5% chance of conversion into round 14.
* Results show that Fnatic will convert a pistol round -> round 2 with a 79.6% chance in <5% of occurrences and 99% in >95% occurrences. 
* Although they are a professional, high-caliber team, this result seems too overconfident. From observation of overall 2026 match data, this isn't the case; they have lost several 2nd rounds after pistol round victories. Thus, use a bigger sample size (e.g. gather data from EMEA kickoff to current) before side conditioning?
* A similar observation can be made in this dataset with the first; 71.9% of converting round 1 -> round 2 in <5% occurrences, and 97.2% round 13 -> round 14 in >95%. 
* The CI is narrower than without the pseudo-trials and adjusted priors, but perhaps it could be narrowed further. 

