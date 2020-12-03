<p align="center">
  <p align="center">
    <a href="https://justdjango.com/?utm_source=github&utm_medium=logo" target="_blank">
      <img src="https://assets.justdjango.com/static/branding/logo.svg" alt="JustDjango" height="72">
    </a>
  </p>
  <p align="center">
    The Definitive Django Learning Platform.
  </p>
</p>

### *** Deprecation warning ***

This project was created almost two years ago. Since then, there is a newer version of the project which you can find [here](https://github.com/justdjango/django-simple-ecommerce)

---

# Django E-commerce

This is a very simple e-commerce website built with Django.

## Quick demo

[![alt text](https://justdjango.s3-us-west-2.amazonaws.com/media/gifs/djecommerce.gif "Logo")](https://youtu.be/z4USlooVXG0)

---

## Project Summary

The website displays products. Users can add and remove products to/from their cart while also specifying the quantity of each item. They can then enter their address and choose Stripe to handle the payment processing.

[![alt text](https://justdjango.s3-us-west-2.amazonaws.com/media/thumbnails/djecommerce.png "Logo")](https://youtu.be/z4USlooVXG0)

---

## Running this project

To get this project up and running you should start by having Python installed on your computer. It's advised you create a virtual environment to store your projects dependencies separately. You can install virtualenv with

```
pip install virtualenv
```

Clone or download this repository and open it in your editor of choice. In a terminal (mac/linux) or windows terminal, run the following command in the base directory of this project

```
virtualenv env
```

That will create a new folder `env` in your project directory. Next activate it with this command on mac/linux:

```
source env/bin/active
```

Then install the project dependencies with

```
pip install -r requirements.txt
```

Now you can run the project with this command

```
python manage.py runserver
```

**Note** if you want payments to work you will need to enter your own Stripe API keys into the `.env` file in the settings files.

---

## Follow the tutorial

This project is part of a [series on YouTube](https://youtu.be/z4USlooVXG0) that teaches how to build an e-commerce website with Django.

---

## Support

If you'd like to support this project and all the other open source work on this organization, you can use the following options

### Option 1: GitHub Sponsors

Sponsor through GitHub Sponsors. On GitHub, [this repository](https://github.com/justdjango/django-ecommerce) shows a button where you can Sponsor the contributors.

### Option 2: JustDjango

If you're learning Django and want to take your next step to become a professional Django developer, consider signing up on [JustDjango](https://learn.justdjango.com).

---

<div align="center">

<i>Other places you can find us:</i><br>

<a href="https://www.youtube.com/channel/UCRM1gWNTDx0SHIqUJygD-kQ" target="_blank"><img src="https://img.shields.io/badge/YouTube-%23E4405F.svg?&style=flat-square&logo=youtube&logoColor=white" alt="YouTube"></a>
<a href="https://www.twitter.com/justdjangocode" target="_blank"><img src="https://img.shields.io/badge/Twitter-%231877F2.svg?&style=flat-square&logo=twitter&logoColor=white" alt="Twitter"></a>

</div>
