# VendorSnap – Automate Your Vendor Discovery 🚀

### "What started as a pain point... became my obsession."

VendorSnap is not just another scraping script — it’s something I built with heart.

While working as a Data Analyst at SK Minerals, I noticed something strange. Our sales team was spending 30–40 minutes manually looking up vendors on IndiaMART, opening 10+ tabs, scrolling endlessly, copying phone numbers into Excel — just for one lead.

It wasn’t just inefficient. It was frustrating, repetitive, and soul-draining. So while others moved on, I didn’t.

I opened my terminal and built something that would change that forever.


## 🧠 What is VendorSnap?

VendorSnap is an automation tool that extracts vendor contact information (names, numbers, product details) directly from IndiaMART search results and exports it to a clean CSV file — no browser needed.

Simple input. Fast output. No more tab-hopping.


## 👨‍💻 Built From Scratch — Every Line, My Own

I built the first prototype on my own — just an idea and a keyboard.  

Then everything broke. My files got corrupted. My cookies expired. IndiaMART’s layout shifted. I almost gave up.

But I couldn’t. Because I had seen what it could do.

So I rebuilt it... from scratch. This time with:
- Persistent cookie-based login
- DOM robustness for changing UIs
- AJAX handling (because phone numbers didn’t load until late)
- Custom retry + validation logic
- Clean CSV export framework

All without any plug-and-play packages — just logic, learning, and sheer willpower to save my team time.



## ⚙️ Features

- 🔐 Cookie-based authentication (survives multiple sessions)
- 🕸️ Parses dynamic AJAX content
- 📤 Clean vendor exports into CSV
- 🔁 Handles HTML layout shifts
- 💡 Optimized for procurement workflows



## 💡Why It Matters

- Manual tasks kill time and motivation
- Automation gives people time back
- A great tool doesn’t need to be flashy — it just needs to *work*

Vendorship workflows don’t have to be messy. VendorSnap makes them smooth, fast, and scalable — especially for operations and sales teams tired of doing copy-paste data entry every day.


## 🛠 Built With
- Python (Requests, BeautifulSoup)
- Cookie-based auth session management
- Custom CLI interface
- Output engine with pandas + CSV export
- 200+ iterations and rebuilding after total file loss


## 🧬 What VendorSnap Represents

✅ Real business pain → converted to code  
✅ Persistence over perfection  
✅ The mindset of a builder, not just a developer

If you’ve ever seen a workflow so broken that you just had to fix it — you already know what VendorSnap is.


## 📁 Sample Output:
| Vendor Name | Phone No | Product | City |
|-------------|----------|---------|------|
| ABC Traders | +91-987XXXXXXX | Zinc Oxide | Mumbai |


## 👋 About Me

Hi, I’m Pratik Bharuka —  
A data analyst who loves transforming repetitive frustration into elegant, working tools.

This is one of my proudest pieces of work — not because it's perfect, but because every part of it was earned.

Let me know what you think!

[LinkedIn](https://linkedin.com/in/pratik-bharuka) • [GitHub](https://github.com/Pratik-source621)
