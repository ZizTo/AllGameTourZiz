from django.shortcuts import render


def need_stuff(in_func):
    def out_func(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated:
            return render(request, "errors/unauthorised.html", {"user": request.user})
        if not request.user.is_staff:
            return render(request, "errors/not_stuff.html", {"user": request.user})

        return in_func(*args, **kwargs)
    return out_func


def need_authorization(in_func):
    def out_func(*args, **kwargs):
        request = args[0]
        if not request.user.is_authenticated:
            return render(request, "errors/unauthorised.html", {"user": request.user})

        return in_func(*args, **kwargs)
    return out_func