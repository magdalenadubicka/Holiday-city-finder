from flask import Flask
from flask_cors import CORS
from flask import request
from vacation_proposer import get_best_cities

app = Flask(__name__)
CORS(app)

@app.route('/api/vacation', methods=['GET'])
def vacation_getter():
  try:
  	checkin_date = request.args.get('checkin')
  	checkout_date = request.args.get('checkout')
  	group_adults = request.args.get('group_adults')
  	group_children = request.args.get('group_children')
  	return get_best_cities(checkin_date, checkout_date, group_adults, group_children), 200
  except Exception as e:
    return str(e), 500

if __name__ == "__main__":
	app.run()
