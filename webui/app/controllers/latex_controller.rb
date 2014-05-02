class LatexController < ApplicationController

  def save_file(examen, filename, content)
    directory = Rails.root.to_s + "/../generated"
    Dir.mkdir(directory) unless File.exists?(directory)
    directory = directory + "/" + examen.directorio
    Dir.mkdir(directory) unless File.exists?(directory)
    filename = directory + "/" + filename
    File.open(filename, "w") do |file|
      file.write(content)
    end
    redirect_to edit_examan_path(examen), :notice => "#{filename} generated successfully"
  end

  def latex_master
    examen = Examan.find(params[:id])
    content = ["% ============================================================================"]
    content << "% #{examen.nombre} "
    content << "% ============================================================================"
    content << "% Lines starting with a % are ignored."
    content << "% Blank lines are ignored as well."
    content << ""
    content << "% the number os questions"
    content << "total: #{examen.cantidad}"
    content << ""
    content << "% the tags that will be used in the test"
    content << "% each tag comes with the minimun number of questions"
    examen.preguntas_por_tema_hash.keys.each do |tag|
      count = examen.preguntas_por_tema_hash[tag]
      string = "@" + tag + ": " + count.to_s
      string += " % warning: this tag has zero question of that type" if count == 0
      content << string
    end
    content << ""
    content << "% here comes the questions"
    content << "--------------------------"
    content << ""

#
#% After all the tags, include the pool of questions.
#% Inside a question blank lines are not ignored, but outputted
#% in the generated LaTeX file
#
#(1)          % Questions start with an alphanumeric identifier in parenthesis.
#@tag1 @tag2  % Next come the question tag(s) in a single line.
#%
#% Next comes the question text, as LaTeX (pure ASCII *is* LaTeX)
#%
#This is the first question, of blah and blah, and blah.
#It contains a long text, that can be split in many lines.
#
#Blank lines are significant outputted to LaTeX, so this text will
#appear in a different paragraph.  % End of line comments work ...
#%
#% ... and inline comments as well. Comments inside a question's
#% text (or answers) are outputted to the LaTeX document.
#%
#_ A line starting with an underscore means a (wrong) answer.
#_x Whereas a line starting with an underscore and an X (any case) means
#   a (right) answer. Answers can span multiple lines too.
#_ Answers are also LaTeX, so you can include complex formulas
#  like this:
#  $$
#    e^{i\pi} + 1 = 0
#  $$
#_x Questions with multiple valid answers are also possible.
#_ Remember to leave (at least) a whitespace before the question text.
#_ You can escape comments with \%, for instance, 100\%.
#
#%
#% All whitespace and comments before the beginning or the end
#% of a question or answer *is* ignored and not outputted to LaTeX.
#%
#
#(2)
#@tag2
#This is the text of the second question.
#_ It has an invalid answer.
#_x A valid answer.
#_ And another invalid answer.
#
#(3)
#@tag3
#This is the text of the third question.
#_x This one is full of valid questions.
#_x Like this one.
#_x And this one.
#_x And this one too.
#_ And a wrong one for the stupid.
#
#(killer-question) % Identifiers need not be numbers.
#% In any case, this will be question 4 in the generated master.tex
#% and the identifiers will be outputted to comments.
#@tag1
#This one is a killer question for all smart-asses out there!
#_ Nope, not this one.
#_ This one neither.
#_ Try again.
#_ Busted!
#% Answers with _* are fixed in that position.
#_* Whoa, no valid answer, is that even possible?
#% And valid answers can also be fixed with _x*
#_x* We wouldn't get that far, but is possible.
#
#(98a7sdh8ydasdkjhas7dagsd) % And you can get creative with identifiers
#@tag4 % It doesn't matter if this tag was not defined, someone will
#      % get it out of pure (lack of) luck.
#This is the fifth question.
#_ Wrong.
#_x Right.
#_ Wrong too.
#
#(6)
#@tag1 @tag3 % We've already shown that multiple tags are possible.
#You can even make a question with only a single answer.
#_x Are you dumb? It's got to be this one...
#
#(many-tags) % Remember to include enough tagged questions such that
#            % the minimum tag restrictions are feasible.
#@tag1 @tag2 @tag3 @tag4
#Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
#tempor incididunt ut labore et dolore magna aliqua.
#
#% Remember that this is LaTeX
#\begin{itemize}
#    \item Ut enim ad minim veniam,
#    \item quis nostrud exercitation ullamco laboris nisi
#    \item ut aliquip ex ea commodo consequat.
#\end{itemize}
#
#\begin{quote}
#    Duis aute irure dolor in reprehenderit in voluptate velit esse
#    cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
#    proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
#\end{quote}
#
#% Creative, right?
#_ This one has a single wrong answer.
    string   = content.join("\n")
    save_file(examen, "master.txt", string)
  end
end
