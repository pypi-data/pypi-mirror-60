{
    "sources": [
        "request.args.get(",
        "request.form.get(",
        "request.get_json(",
        "request.url",
        ".data",
        "form[",
        "form(",
        "Markup(",
        "cookies[",
        "files[",
        "SQLAlchemy"
    ],
    "sinks": {
        "system(": {
            "sanitisers": [
                "shlex.split",
                "shlex.quote"
            ]
        },
        "call(": {
            "sanitisers": [
                "shlex.split",
                "shlex.quote"
            ]
        },
        "Popen(": {
            "sanitisers": [
                "shlex.split",
                "shlex.quote"
            ]
        }
    }
}