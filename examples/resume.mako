% for contact in d["contact"]:
${contact['name']}
${contact['phone']}
${contact['email']}
${contact['www']}
% endfor
=========================================

SKILLS:
-------
% for skill in d["skills"]:
  ${skill['type']}: 
    ${s._wrap(2,skill['skill_list'])}
% endfor

EDUCATION:
----------
% for e in d['education']:
  ${e['degree']} from ${e['university']} in ${e['field']} (${e['date']})
% endfor

EXPERIENCE:
----------
% for e in d['experience']:
  ${e['position']} (${e['date']})
  ${e['company']}, ${e['location']}
  -----------------------------------
    ${s._wrap(2,e['summary'])}

% endfor

