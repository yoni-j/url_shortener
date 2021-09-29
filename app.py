from shortened import Shortened

from flask import Flask, jsonify, redirect, request, make_response
import requests

app = Flask(__name__)

shortened = Shortened()


@app.route('/shorten_url', methods=['POST'])
def shorten_url():
    if not request.json:
        return shortened.bad_request('Url must be provided in json format.')

    if 'url' not in request.json:
        return shortened.bad_request('Url parameter not found.')

    url = request.json['url']
    if url[:4] != 'http':
        url = 'http://' + url

    if not shortened.url_valid(url):
        return shortened.bad_request('Provided url is not valid.')

    shortened_url = shortened.shorten(url)
    shortened.shortened[shortened_url] = {"url": url, "click_counter": 0, "unique_counter": 0, "countries": set()}
    country = requests.get(f"https://freegeoip.app/json/").json()["country_name"]
    shortened.shortened[shortened_url]["countries"].add(country)

    return jsonify({'shortened_url': shortened_url}), 201


@app.route('/<alias>', methods=['GET'])
def get_shortened(alias):
    if alias not in shortened.shortened:
        return shortened.bad_request('Unknown alias.')

    url = shortened.shortened[alias]["url"]
    shortened.shortened[alias]["click_counter"] += 1
    if not request.cookies.get(alias):
        shortened.shortened[alias]["unique_counter"] += 1
    res = make_response()
    res.set_cookie(alias, value=alias)

    return redirect(url, code=302)


@app.route('/count/<alias>', methods=['GET'])
def count(alias):
    return jsonify({'count': shortened.counter(alias)}), 200


@app.route('/unique_clicks/<alias>', methods=['GET'])
def unique_clicks(alias):
    return jsonify({'count': shortened.unique_clicks(alias)}), 200

@app.route('/get_countries/<alias>', methods=['GET'])
def get_countries(alias):
    return jsonify({'countries': list(shortened.get_countries(alias))}), 200


if __name__ == '__main__':
    app.run(debug=True)
