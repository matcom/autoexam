module ApplicationHelper

  def buena_etiqueta(etiqueta)
    etiqueta.gsub(/[^a-zA-Z0-9]/, '-').gsub(/-+/,'-')
  end

  def etiquetas_de(object)
    string = ""
    for etiqueta in object.listado_de_etiquetas
      string += %<<span class="label">#{etiqueta}</span>  >
    end
    string.html_safe
  end
end
