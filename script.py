import requests

URL = "http://codeforces.com/api/"
RATING_CHANGE = 100


def send_get_request(offset):
	try:
		resp = requests.get(URL + offset)
		resp.raise_for_status()
	except Exception as err:
		print(f"Error occurred: {err}")
	return resp.json()


def get_users_submissions(users):
	"""
	- users: List of users
	- Returns set of attempted problems by any user in users
	"""
	submissions_data = set()
	for user in users:
		user_data = send_get_request("user.status?handle=" + user)["result"]
		for obj in user_data:
			problem = obj["problem"]
			submissions_data.add((problem["contestId"], problem["index"]))
	return submissions_data


def parse_required_problems(lo, hi, users_data):
	"""
	- lo: Lower rating bound
	- hi: Upper rating bound
	- users_data: Set of problems to be excluded from result
	- Returns list of parsed problems from cf one from each rating in [lo, hi]
	- Problem with more submissions count is preffered
	- [x rating problem, x + RATING_CHANGE rating problem, ...]
	"""
	problems_data = send_get_request("problemset.problems")["result"]
	problems_statistics = problems_data["problemStatistics"]
	problems = problems_data["problems"]
	parsed_problems = ["No problem available" for rating in range(lo, hi + RATING_CHANGE, RATING_CHANGE)]
	max_solved_count = [-1 for rating in range(lo, hi + RATING_CHANGE, RATING_CHANGE)]
	for ind in range(0, len(problems)):
		if "rating" not in problems[ind]:
			continue
		parsed_problem = {
			"contest_id": problems[ind]["contestId"],
			"index": problems[ind]["index"],
			"name": problems[ind]["name"],
			"rating": problems[ind]["rating"],
			"solved_count": problems_statistics[ind]["solvedCount"]
		}
		if (parsed_problem["contest_id"], parsed_problem["index"]) in users_data:
			continue
		problem_rating = parsed_problem["rating"]
		if lo <= problem_rating and problem_rating <= hi:
			tar_position = (problem_rating - lo) // 100
			if parsed_problem["solved_count"] > max_solved_count[tar_position]:
				max_solved_count[tar_position] = parsed_problem["solved_count"]
				parsed_problems[tar_position] = str(parsed_problem["contest_id"]) + parsed_problem["index"]
	return parsed_problems
			

if __name__ == "__main__":
	users_list = input("Enter the handles of users: ").split()
	rating_range = list(map(int, input("Enter the rating range of problems [lower_rating upper_rating]: ").split()))
	users_data = get_users_submissions(users_list)
	problems_list = parse_required_problems(rating_range[0], rating_range[1], users_data)
	rating = rating_range[0]
	for problem in problems_list:
		print(f"{rating}: {problem}")
		rating += RATING_CHANGE
