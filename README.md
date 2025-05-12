Hey there!

So, if you’d asked me two weeks ago (or really at any time earlier), "Hubert, what do you think you'll be doing the weekend before graduation?" The absolute last thing I would have imagined was spending that weekend diving into back-testing and tuning a Smart Order Router. But here we are! And honestly, I couldn’t be happier. This project pushed me to the limits, and looking back, I can tell one thing for sure and that it was a ton of fun!

Now, here's the thing, I’m not 100% confident in my code or my README just yet, but I’m hopeful that what I’ve put together meets the expectations. If not, no worries! I’m all ears for feedback. I wanted to give you a quick rundown of what I bring to the table as an intern:

1. No Cost, Just the Opportunity: I’m offering to work part-time, in person, and for free. All I want is the chance to work with you and build up my knowledge and skillset. SO even if you think my Python skills are questionable TRUST ME, I will provide value before the end of the summer to the firm, and it would be even easier to do so if you all don't pay me a dime.
   
2. Quick Learner: Sure, everyone says that, but I’ve got some solid proof. My Post-Docs and PI (my professor) even said I should get an honorary electrical engineering degree for the work I did in my Master's program. And trust me, that’s coming from someone who didn’t know how a breadboard worked back in month 4 of my program!
   
3. Humility and Hunger to Learn: I know I still have so much to learn, and I'm not afraid to dive into the grunt work that others might avoid. I may ask a few "dumb" questions, but hey – I’d rather get them out of the way than pretend I know everything!

Long story short: I’m thankful for this opportunity, I’m not perfect, but I’m ready to learn and grow. Now, let’s dive into the project itself! (See below)

This project explores how to split a large parent order across multiple trading venues using Level 1 market data, aiming to minimize execution costs. The method evaluates all valid order splits using a cost function that penalizes:

Overfills – sending more than a venue can realistically fill

Underfills – not sending enough to fully execute the parent order

Queue position uncertainty – the chance that an order won’t fill due to depth

Three parameters were tuned:

λ_over: overfill penalty

λ_under: underfill penalty

θ_queue: queue risk penalty

Each of these parameters was tested at two levels: 0.001 and 0.01. This range was chosen to strike a balance between computational efficiency and meaningful variation. It spans from lenient (low penalty) to moderately strict (higher penalty), allowing us to observe the sensitivity of the strategy to small changes in penalty weight without overwhelming the model with excessive combinations or extreme values. This approach helps prevent overfitting while still ensuring the model accounts for real-world trading conditions.

Future improvement: Slippage modeling

To improve fill realism, we propose incorporating slippage. A simple model would increase the expected ask price based on the order size relative to available depth (e.g., a 0.1% markup per 1,000 shares over book depth), reflecting how large orders often fill at worse prices in real markets.

Thanks for taking the time to check this out! While I’m still learning and improving, I’m really excited about the potential of this project and the opportunity to work with you. 

Cheers,
Hubert Sliwka
