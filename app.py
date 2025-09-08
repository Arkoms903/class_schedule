from flask import Flask, render_template, request, flash
from scheduler import build_schedule, format_schedule, DAYS

app = Flask(__name__)
app.secret_key = "supersecret"   # needed for flash messages


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Basic inputs
            sections = int(request.form["sections"])
            periods_per_day = int(request.form["periods"])
            num_subjects = int(request.form["num_subjects"])
            num_faculty = int(request.form["num_faculty"])
            num_classrooms = int(request.form["classrooms"])

            # 🔹 Validation
            if sections <= 0 or periods_per_day <= 0 or num_subjects <= 0 or num_faculty <= 0 or num_classrooms <= 0:
                flash("All inputs must be positive integers!", "error")
                return render_template("index.html")

            # Collect subjects + weekly quotas
            subjects = []
            weekly_quota = {}
            for i in range(num_subjects):
                s = request.form[f"subject_{i}"].strip()
                if not s:
                    flash("Subject name cannot be empty!", "error")
                    return render_template("index.html")

                theory = int(request.form[f"subject_{i}_theory"])
                practical = int(request.form[f"subject_{i}_practical"])

                if theory < 0 or practical < 0:
                    flash(f"Invalid weekly quota for {s}", "error")
                    return render_template("index.html")

                subjects.append(s)
                weekly_quota[s] = {"T": theory, "P": practical}

            # Faculties
            faculty = {}
            subject_to_fac = {}
            for i in range(num_faculty):
                fname = request.form[f"faculty_{i}_name"].strip()
                nsubs = int(request.form[f"faculty_{i}_subs"])

                if not fname:
                    flash("Faculty name cannot be empty!", "error")
                    return render_template("index.html")
                if nsubs <= 0:
                    flash(f"Faculty {fname} must teach at least one subject!", "error")
                    return render_template("index.html")

                fac_subjects = []
                for j in range(nsubs):
                    s = request.form[f"faculty_{i}_sub_{j}"]
                    if s not in subjects:
                        flash(f"Faculty {fname} assigned unknown subject {s}", "error")
                        return render_template("index.html")
                    fac_subjects.append(s)
                    subject_to_fac[s] = fname
                faculty[fname] = fac_subjects

            # Classrooms
            classrooms = [f"CR{i+1}" for i in range(num_classrooms)]

            # Sections (A, B, C, …)
            section_list = [chr(65 + i) for i in range(sections)]

            # Build schedules
            schedules = build_schedule(
                section_list, subjects, faculty, subject_to_fac,
                weekly_quota, periods_per_day, classrooms
            )

            # Format schedules for HTML
            formatted = {sec: format_schedule(schedules[sec], periods_per_day) for sec in section_list}
            return render_template("timetable.html", schedules=formatted, days=DAYS, periods=periods_per_day)

        except Exception as e:
            flash(f"Error: {e}", "error")
            return render_template("index.html")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)