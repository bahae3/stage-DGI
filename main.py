# Install the following packages via your terminal:
# pip install flask flask_mysqldb

import pprint
from collections import Counter
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
            (r.MONTANT_TVA - d.MNT_DEDUCTION) AS ecart
        FROM 
            Releve_deduction_edi r
        JOIN 
            Declaration d ON r.ID_DECLARATION = d.ID_DECLARATION
        WHERE 
            d.ANNEE_DECLAR = %s AND
            d.DATE_DEPOT BETWEEN %s AND %s;
        """
        cur.execute(query, (annee, deAnnee, aAnnee))  # query execution
        all_data = cur.fetchall()  # data stocked in a tuple
        cur.close()

        list_data = []  # this list will store the data that we need in a list, not a tuple
        for i in all_data:
            row_list = []
            for j in i:
                row_list.append(j)
            list_data.append(row_list)
        return render_template("ecart.html", all_data=list_data)
    return render_template("ecart.html")


# Activités contribuables
@app.route("/activites_contribuables", methods=['GET', 'POST'])
def activites_contribuables():
    if request.method == "POST":
        id_fiscal = request.form.get("if")
        annee = request.form.get("annee")
        print(f"if: {id_fiscal} - annee: {annee}")

        cursor = mysql.connection.cursor()
        # This query selects the activities from table "declaration"
        # with a join of table "adherent" and table "activites"
        query = """
                    SELECT d.ID_DECLARATION, a.id_fiscal, a.nom_prenom_rs, ac.libelle,d.periode_declar, d.annee_declar, d.regime_declar
                    FROM declaration d 
                    JOIN adherent a on a.ID_ADHERENT = d.ID_ADHERENT
                    JOIN activites ac on ac.ID_ADHERENT = a.ID_ADHERENT
                    WHERE a.id_fiscal=%s AND d.annee_declar=%s
                    GROUP BY d.ID_DECLARATION;
                """
        cursor.execute(query, (id_fiscal, annee))
        results = cursor.fetchall()

        # Storing result in a list
        adherent_data = []
        for row in results:
            taxpayer_info = {
                'ID_DECLARATION': row[0],
                'ID_FISCAL': row[1],
                'RESEAU_SOCIAL': row[2],
                'ACTIVITE': row[3],
                'PERIODE': row[4],
                'ANNEE': row[5],
                'REGIME': row[6]
            }
            adherent_data.append(taxpayer_info)

        # Count occurrences of 'ACTIVITE'
        activity_counter = Counter(item['ACTIVITE'] for item in adherent_data)
        pprint.pprint(activity_counter)

        # Change this variable's value if you want activities to appear more than twice
        fois = 2

        # Filter adherent_data to include only items where ACTIVITE appears exactly 2 times
        filtered_activities = {item['ACTIVITE'] for item in adherent_data if activity_counter[item['ACTIVITE']] == fois}

        # Create unique_filtered_data containing one instance of each filtered ACTIVITE
        unique_filtered_data = []
        for activity in filtered_activities:
            for item in adherent_data:
                if item['ACTIVITE'] == activity:
                    unique_filtered_data.append(item)
                    break  # Stop after adding the first instance

        # pprint.pprint(unique_filtered_data)
        # pprint.pprint(adherent_data)
        return render_template("activites.html", activites=unique_filtered_data)
    return render_template("activites_form.html")


# Comparaison crédit déclaré vs crédit calculé
@app.route('/comparer_credit')
def comparer_credit():
    cursor = mysql.connection.cursor()
    # This query calculates the declared credit amount and the sum of tva prorata amounts
    # for each tax declaration in the system
    ## I inserted new examples in the db to see the results ##
    query = """
            SELECT
                d.ID_DECLARATION,
                a.ID_FISCAL,
                d.MNT_CREDIT AS Declared_Credit,
                SUM(r.MONTANT_TVA_PRORATA) AS Calculated_Credit
            FROM
                declaration d
            LEFT JOIN
                releve_deduction_edi r ON d.ID_DECLARATION = r.ID_DECLARATION
            LEFT JOIN 
            	adherent a ON d.ID_ADHERENT = a.ID_ADHERENT
            GROUP BY
                d.ID_DECLARATION, d.MNT_CREDIT
            HAVING
                Calculated_Credit IS NOT NULL
            AND
                a.ID_FISCAL IS NOT NULL;
        """

    cursor.execute(query)
    results = cursor.fetchall()
    # pprint.pprint(results)
    cursor.close()

    # the wanted data is stored in this list, to be used in the webpage comparaison.html
    comparison_data = []
    for result in results:
        comparison_data.append({
            'ID_DECLARATION': result[0],
            'ID Fiscal': result[1],
            'Crédit déclaré': float(result[2]),
            'Crédit calculé': result[3],
            'Ecart': result[3] - float(result[2])
        })
    # pprint.pprint(comparison_data)
    return render_template("comparaison.html", comparaisons=comparison_data)


# Info d'une declaration cliquee dans la comparaison des credits
@app.route("/info", methods=['GET', 'POST'])
def info():
    id_declar = request.args.get('id_declar')
    cursor = mysql.connection.cursor()
    query = """
                SELECT d.ID_DECLARATION, 
                d.ID_ADHERENT, 
                a.NOM_PRENOM_RS, 
                d.ANNEE_DECLAR, 
                d.PERIODE_DECLAR, 
                d.REGIME_DECLAR 
                FROM declaration d 
                JOIN adherent a ON a.ID_ADHERENT=d.ID_ADHERENT 
                WHERE a.NOM_PRENOM_RS != "test"
                AND d.ID_DECLARATION=%(id_declar)s;
            """

    cursor.execute(query, {'id_declar': id_declar})
    results = cursor.fetchall()
    cursor.close()
    print(results)

    declar_info = {
        'ID_DECLARATION': results[0][0],
        'ID Adherent': results[0][1],
        'NOM_PRENOM_RS': results[0][2],
        'ANNEE_DECLAR': results[0][3],
        'PERIODE_DECLAR': results[0][4],
        'REGIME_DECLAR': results[0][5]
    }

    # pprint.pprint(declar_info)
    return render_template("declaration_info.html", declar_info=declar_info)


# function to convert from yyyy-mm-dd to dd-mm-yyyy
def convert_date(date):
    try:
        date_unformatted = datetime.strptime(str(date), '%Y-%m-%d')
        formatted_date = date_unformatted.strftime('%Y-%m-%d')
        return formatted_date
    except ValueError:
        return "Format de date invalide.", 400


if __name__ == "__main__":
    app.run(debug=True)
