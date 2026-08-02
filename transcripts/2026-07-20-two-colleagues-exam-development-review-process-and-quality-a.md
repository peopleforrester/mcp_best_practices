<!-- ABOUTME: Routed transcript (My recording 80.mp3), matched to this repo on 2026-07-20. -->
<!-- ABOUTME: Auto-routed because: 1 section(s) of this conversation match the mcp_best_practices topic. Raw diarization; speaker labels are approximate. -->

# Two colleagues - Exam development review process and quality assurance

_Routed from the transcription pipeline on 2026-07-20. Source: My recording 80.mp3._

---

### Review of protocol primitives items

Speaker 1: Protocol primitives.

Speaker 3: According to MCP design principles for test. Other than a resource. Well, I mean, resources are read only. Alright, so, looking at ServerStrike, we've got the brand new ticket inside of the customer tracking system, running a localized search function, so that's read-only, querying an external database, that's read-only, checking a remote endpoint to read the current online-offline status of device, that's read-only, looking at a ServerScript that creates, yep, that's 100% why you would use a tool. So, yeah, yeah, yeah,

Speaker 1: One correct and three wrong.

Speaker 3: those are good too. Oh man, that's really good, except like you have to know. That resources are read-only and you have to be able to interpret those as read-only entries. That's that's good. Yeah So sorry earlier. Do you have a 1230 meeting because I just want to acknowledge it's 1230

Speaker 1: No, no, no, no. I have the top of the hour.

Speaker 3: Ah, okay good. I can go to the top of our hour too if you want

Speaker 1: I'll probably go to about 10 still if you don't mind because then it gives me a chance to decompress and think about conflict

Speaker 3: Oh, you know what? I have my other meeting at top of the hour, so that works out for me too, actually. I'm just looking at my work laptop. Yeah.

Speaker 1: Okay, so this is protocol primitives

Speaker 4: We're on primitives. Oh, we're on we're back to tools and resources. Okay. Interesting. Does require payment while resources are free. Tools use natural language while resources use. Those were on client while resources were on servers. I think that's accurate.

Speaker 5: Yeah.

Speaker 4: I mean, rules perform actions and resources provide data. Is that the way we think about it? Is that the way it's written? I might have to look at the spec, but I think, I mean, I think that's good enough. I don't want to overthink it. You know how engineers kind of overthink something.

Speaker 5: Okay.

Speaker 4: I think that's great,

Speaker 5: And

Speaker 4: actually.

Speaker 5: also

Speaker 4: I just was like running it

Speaker 5: it

Speaker 4: past you.

Speaker 5: can render data and see how it performs there too. See if it's okay.

Speaker 4: Yeah, I mean, it's

Speaker 5: I wonder if overthink will find the definition.

Speaker 4: right on the edge of overthinking. over simplifying but I don't know that it is over simplifying right it is yeah I would see how it doesn't have but I I don't know if you have a way of flagging like hey extra attention but yeah

Speaker 5: I do flag on my team. I change notes on my spreadsheet.

Speaker 4: yeah I would flag this one as like how did this really do in beta there's like the other ones we've looked at are clean but this one I'm kind of like maybe yeah

Speaker 5: That was pretty good. It is the simplest of importability.

Speaker 4: The ability of a server to change network protocols during an active user session, no, they can't do that dynamically. The ability of a server to convert upstream protocol to a different file format. Auto-weights, hmm. That would be amazing if it could do that, but that's not possible. The ability of a server to synchronize user convention logs across. Like a host problem.

Speaker 5: Yeah.

Speaker 4: The ability of a server to connect to different client applications without rewriting. Yes. That's true, right? That's the whole reason, right, for the MCP compliance. Without modification, it's like write once, plug it anywhere kind of property. So, yeah, that looks good.

Speaker 5: Okay, so one correct and three wrong.

Speaker 4: Yep.
