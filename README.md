<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a id="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->


<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h1>Wordle Solver</h1>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#how-it-works">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>


<!-- ABOUT THE PROJECT -->
## About The Project

Wordle at its core is a simple game. But when you come across a word like PARER... its not the most fun experience. To combat this, I decided to solve wordle in a systematic way while also giving individuals a space for high pressure practice.

Introducing my own Wordle practice bot! You can test it below here.
https://wordlepractice.vercel.app/

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

This section should list any major frameworks/libraries used to bootstrap your project. Leave any add-ons/plugins for the acknowledgements section. Here are a few examples.

* [![React][React.js]][React-url]
* [![Flask][Flask]][Flask-url]


<p align="right">(<a href="#readme-top">back to top</a>)</p>


<h2 id="usage">Usage</h2>

<div align="center">
  <img src="images/WordlePractice.gif" alt="Wordle Solver Demo" width="600"/>
</div>

The main page is a place where you can practice Wordle solutions as many times as you want with our algorithm help.

<div align="center">
  <img src="images/WordlePractice.gif" alt="Wordle Solver Demo" width="600"/>
</div>
<div align="center">
  <img src="images/WordlePractice.gif" alt="Wordle Solver Demo" width="600"/>
</div>

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<h2 id="how-it-works">How It Works</h2>

The solver always chooses the guess that minimizes the expected number of answers left.  

1. **Start with all candidates.** At the beginning, every word in the solution pool is possible.  
2. **Simulate each guess.** For every candidate word, pretend it is the secret answer and compute the feedback (🟩/🟨/⬜) it would produce against all other words.  
3. **Group by feedback pattern.** Words that yield the same feedback form a “bucket” (e.g., 🟩⬜🟨⬜⬜).  
4. **Calculate expectation.** For each bucket, multiply its size by its probability (bucket size ÷ total). Adding these gives the *expected remaining pool size* if that word were guessed.  
5. **Pick the best guess.** Choose the word with the lowest expectation.  
6. **Repeat until solved.** Continue updating the pool and repeating the process until only one candidate remains, or until it is efficient to guess directly.  

This approach is similar to *20 Questions*: each guess partitions the space of answers, and the best guess is the one that splits the space most evenly.


<h2 id="contributing">Contributing</h2>

Contributions are welcome! This solver is meant to be both an **educational tool** and a **fun project**, so improvements of all kinds are appreciated:

- 🧮 Algorithm optimizations (faster pruning, new heuristics, etc.)  
- 🎨 Frontend/UI improvements (better layout, animations, styling)  
- 📊 New features (stats tracking, hard mode, challenge modes)  
- 📝 Documentation updates or clearer explanations  

If you’d like to help, here’s the suggested workflow:

1. **Fork** the repository  
2. **Create a feature branch** (`git checkout -b feature/YourFeatureName`)  
3. **Commit** your changes (`git commit -m 'Add feature: YourFeatureName'`)  
4. **Push** to your branch (`git push origin feature/YourFeatureName`)  
5. **Open a Pull Request** describing what you’ve added  

Even small contributions — like fixing typos or improving explanations — make a big difference.  
And if you find the project useful, don’t forget to ⭐️ star the repo!


<h2 id="contact">Contact</h2>

Richard Guo - rwg2125@columbia.edu

Project Link: [https://github.com/RichardGuo24/WordleBotPractice](https://github.com/RichardGuo24/WordleBotPractice)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<h2 id="acknowledgments">Acknowledgments</h2>

Shout out to the friends at Jane Street that helped me get started on this project over a year ago. Came back to improve on the algorithm and also put it on a fullstack application.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



[contributors-shield]: https://img.shields.io/github/contributors/othneildrew/Best-README-Template.svg?style=for-the-badge
[contributors-url]: https://github.com/othneildrew/Best-README-Template/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/othneildrew/Best-README-Template.svg?style=for-the-badge
[forks-url]: https://github.com/othneildrew/Best-README-Template/network/members
[stars-shield]: https://img.shields.io/github/stars/othneildrew/Best-README-Template.svg?style=for-the-badge
[stars-url]: https://github.com/othneildrew/Best-README-Template/stargazers
[issues-shield]: https://img.shields.io/github/issues/othneildrew/Best-README-Template.svg?style=for-the-badge
[issues-url]: https://github.com/othneildrew/Best-README-Template/issues
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/othneildrew/Best-README-Template/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/othneildrew
[product-screenshot]: images/screenshot.png
[React.js]: https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB
[React-url]: https://reactjs.org/
[Flask]: https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/
will be ignored by the browser. -->
