const uploader = `
<div class="uploader">
<input class="form-control file-input" type="file" id="formFile" name="file%%" required />
<input class="user-input name form-control" type="text" id="fontName%%" name="name%%" placeholder="Font Family" required />
<label class="form-check-label select-label" for="style%%">Italic: </label>
<select name="style%%" class="user-input form-select dropdown" id="style%%">
<option value="normal" selected>normal</option>
<option value="italic">italic</option>
</select>
<label class="form-check-label select-label" for="weight%%">Weight: </label>
<select name="weight%%" class="user-input form-select dropdown" id="weight%%">
<option value="normal" selected>normal</option>
<option value="bold">bold</option>
<option value="thin">thin</option>
<option value="heavy">heavy</option>
</select>
</div>
`

let uploaderCount = 1;


function addUploader() {
  if(uploaderCount > 9) return;

  const form = document.getElementById('fontForm');
  const newUploader = uploader.replaceAll('%%', uploaderCount.toString());
  form.insertAdjacentHTML('beforeend', newUploader)
  uploaderCount += 1;
}


function removeLastUploader() {
  const uploaders = document.querySelectorAll('.uploader');
  if(uploaders.length <= 1) return;
  
  const lastUploader = uploaders[uploaders.length - 1];
  lastUploader.parentNode.removeChild(lastUploader);
  uploaderCount -= 1;
}

