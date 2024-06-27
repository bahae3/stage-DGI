# Install the following packages via your terminal:
# pip install flask flask_mysqldb

import pprint
from datetime import datetime
from flask import Flask, render_template, request
from flask_mysqldb import MySQL

# creating the app
app = Flask(__name__)
app.config['SECRET_KEY'] = "bahae03"
app.app_context().push()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# connect to database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'stage24'  # my db name is stage24

mysql = MySQL(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/admin")
def admin():
    return render_template("admin.html")


# Ecart entre déduction facturée et deduction déclarée
@app.route("/ecart", methods=['GET', 'POST'])
def ecart():
    # retrieving data from form in ecart.html
    if request.method == "POST":
        annee = request.form.get("annee")
        # I used a function that I created that converts date format 'convert_date()'
        deAnnee = convert_date(request.form.get("fromDate"))
        aAnnee = convert_date(request.form.get("toDate"))

        # I'm using the retrieved data to manipualte the database
        cur = mysql.connection.cursor()
        query = """
        SELECT 
            d.ID_DECLARATION, 
            r.NUM_FACTURE, 
            r.MONTANT_TVA AS deduction_facturee, 
            d.MNT_DEDUCTION AS deduction_declaree, 
            (r.MONTANT_TVA - d.MNT_DEDUCTION) AS difference
        FROM 
            Releve_deduction_edi r
        JOIN 
            Declaration d ON r.ID_DECLARATION = d.ID_DECLARATION
        WHERE 
            d.ANNEE_DECLAR = %s AND
            d.DATE_DEPOT BETWEEN %s AND %s;
        """
        cur.execute(query, (annee, deAnnee, aAnnee))  # query execution
        all_data = cur.fetchall()
        cur.close()

        list_data = []  # this list will store the data that we need
        for i in all_data:
            row_list = []
            for j in i:
                row_list.append(j)
            list_data.append(row_list)
        return render_template("ecart.html", all_data=list_data)
    return render_template("ecart.html")


# Activités contribuables
@app.route("/activites_contri")
def activites():
    cursor = mysql.connection.cursor()
    query = """
                SELECT a.ID_ADHERENT, a.NOM_PRENOM_RS, a.ID_ACTIVITE,
                       d.ID_DECLARATION, d.MNT_CREDIT,
                       r.ID, r.MONTANT_TVA_PRORATA
                FROM adherent a
                LEFT JOIN declaration d ON a.ID_ADHERENT = d.ID_ADHERENT
                LEFT JOIN releve_deduction_edi r ON d.ID_DECLARATION = r.ID_DECLARATION
            """

    cursor.execute(query)
    results = cursor.fetchall()

    adherent_data = []
    for row in results:
        taxpayer_info = {
            'ID_ADHERENT': row[0],
            'NOM_PRENOM_RS': row[1],
            'ID_ACTIVITE': row[2],
            'DECLARATIONS': []
        }

        if row[3] is not None:  # Check if there is a declaration linked
            declaration = {
                'ID_DECLARATION': row[3],
                'MNT_CREDIT': float(row[4]) if row[4] is not None else None,
                'DEDUCTIONS': []
            }

            if row[5] is not None:  # Check if there is a deduction linked
                deduction = {
                    'ID_DEDUCTION': row[5],
                    'MONTANT_TVA_PRORATA': float(row[6]) if row[6] is not None else None
                }
                declaration['DEDUCTIONS'].append(deduction)

            taxpayer_info['DECLARATIONS'].append(declaration)

        adherent_data.append(taxpayer_info)
    pprint.pprint(adherent_data)
    print(len(adherent_data))
    # return jsonify(adherent_data)
    return render_template("activites.html", activites=adherent_data)


# Comparaison crédit déclaré vs calculé
@app.route('/comparer_credit')
def comparer_credit():
    cursor = mysql.connection.cursor()
    # This query calculates the declared credit amount and the sum of tva prorata amounts
    # for each tax declaration in the system
    ## I inserted new examples in the db to see the results ##
    query = """
            SELECT
                d.ID_DECLARATION,
                d.MNT_CREDIT AS Declared_Credit,
                SUM(r.MONTANT_TVA_PRORATA) AS Calculated_Credit
            FROM
                declaration d
            LEFT JOIN
                releve_deduction_edi r ON d.ID_DECLARATION = r.ID_DECLARATION
            GROUP BY
                d.ID_DECLARATION, d.MNT_CREDIT
            HAVING
                Calculated_Credit IS NOT NULL
        """

    cursor.execute(query)
    results = cursor.fetchall()

    # the wanted data is stored in this list, to be used in the webpage comparaison.html
    comparison_data = []
    for result in results:
        comparison_data.append({
            'ID_DECLARATION': result[0],
            'Crédit déclaré': float(result[1]),
            'Crédit calculé': result[2],
            'Différence (cd - cc)': float(result[1]) - result[2]
        })
    # pprint.pprint(comparison_data)
    return render_template("comparaison.html", comparaisons=comparison_data)


# function to convert from yyyy-mm-dd to dd-mm-yyyy
def convert_date(date):
    try:
        date_unformatted = datetime.strptime(str(date), '%Y-%m-%d')
        formatted_date = date_unformatted.strftime('%d-%m-%Y')
        return formatted_date
    except ValueError:
        return "Format de date invalide.", 400


if __name__ == "__main__":
    app.run(debug=True)
