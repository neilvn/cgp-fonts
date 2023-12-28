import boto3
import os

from flask import (
    Flask, 
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from functions import (
    convert_form,
    get_all_ddb_items,
    font_in_families,
    font_in_fonts,
    save_family_to_ddb,
    save_font_to_ddb,
    upload_file
)

from constants import (
    AUTH_KEY,
    CUSTOMER_KEY,
    NAME_KEY
)


app = Flask(__name__)

app.secret_key = os.environ.get('SECRET_KEY')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get(AUTH_KEY):
            return redirect(url_for('index'))
        
        return render_template('login.html', failed=False)

    if (
        request.form.get('username') == os.environ.get('SITE_USERNAME')
        and request.form.get('password') == os.environ.get('SITE_PASSWORD')
    ):
        session[AUTH_KEY] = True
        return redirect(url_for('index'))
    
    return render_template('login.html', failed=True)


@app.route('/')
def index():
    if not session.get(AUTH_KEY):
        return redirect(url_for('login'))

    return render_template('index.html')  


@app.route('/upload', methods=['POST'])
def upload():
    if not session.get(AUTH_KEY):
        return make_response('<h1>Access Denied</h1>', 401)
    
    dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

    form_dict = convert_form(request)
    
    fonts_table = dynamodb.Table(os.environ.get("FONT_TABLE"))
    families_table = dynamodb.Table(os.environ.get("FAMILY_TABLE"))
    
    fonts = get_all_ddb_items(fonts_table)
    families = get_all_ddb_items(families_table)

    customer_id = form_dict[CUSTOMER_KEY]

    results = []

    for form in form_dict:
        if form == CUSTOMER_KEY:
            continue

        family_id = font_in_families(form_dict[form][NAME_KEY], families)

        status = 'Success'

        # Family does not exist, create both family and font
        if not family_id:
            try:
                upload_file(
                    request.files[f'file{form}'],
                    customer_id
                )
                new_family_id = save_family_to_ddb(
                    families_table,
                    form_dict[form],
                    customer_id
                )
                save_font_to_ddb(
                    fonts_table,
                    form_dict[form],
                    new_family_id,
                    customer_id,
                    request.files[f'file{form}']
                )
            except:
                status = 'Error'
        
            results.append({ 'form': form_dict[form], 'status': status})
        
        # Exact font type exists, is duplicate
        elif font_in_fonts(family_id, form_dict[form], fonts):
            results.append({ 'form': form_dict[form], 'status': 'Duplicate' })
            continue
            
        # Family exists but not font type
        else:
            try:
                upload_file(
                    request.files[f'file{form}'],
                    customer_id
                )
                save_font_to_ddb(
                    fonts_table,
                    form_dict[form],
                    family_id,
                    customer_id,
                    request.files[f'file{form}']
                )
            except:
                status = 'Error'

            results.append({ 'form': form_dict[form], 'status': status })
            

    return render_template('status.html', results=results)


if __name__ == '__main__':
    app.run()
